import xmlrpc.client
from flask import current_app


class OdooConnector:
    def __init__(self):
        self.url = current_app.config.get("ODOO_URL")
        self.db = current_app.config.get("ODOO_DB")
        self.username = current_app.config.get("ODOO_USERNAME")
        self.password = current_app.config.get("ODOO_PASSWORD")
        self.uid = None
        self.models = None

    def connect(self):
        if not all([self.url, self.db, self.username, self.password]):
            raise ValueError("Config Odoo incompleta")
        common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self.uid = common.authenticate(self.db, self.username, self.password, {})
        if not self.uid:
            raise ValueError("Autenticación Odoo fallida")
        self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")
        return True

    def ping(self) -> bool:
        if self.models is None:
            self.connect()
        return True

    def search_read(self, model: str, domain: list, fields: list, limit: int = 0):
        if self.models is None:
            self.connect()
        return self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            model,
            'search_read',
            [domain],
            {'fields': fields, 'limit': limit}
        )

    def get_unpaid_invoices(self, limit: int = 0, start_date: str | None = None, end_date: str | None = None, customer: str | None = None):
        domain = [
            ['move_type', '=', 'out_invoice'],
            ['state', '=', 'posted'],
            ['payment_state', 'in', ['not_paid', 'partial']]
        ]
        if start_date:
            domain.append(['invoice_date', '>=', start_date])
        if end_date:
            domain.append(['invoice_date', '<=', end_date])
        if customer:
            domain.append(['partner_id', 'ilike', customer])
        fields = [
            'name', 'partner_id', 'invoice_date', 'invoice_date_due',
            'amount_total', 'amount_residual', 'currency_id', 'invoice_origin',
            'l10n_latam_document_type_id', 'move_type'
        ]
        return self.search_read('account.move', domain, fields, limit=limit)

    def get_report_lines(self, start_date: str | None = None, end_date: str | None = None, customer: str | None = None, limit: int = 0):
        # Query account.move.line focused on receivable lines (with fallbacks)
        base_domain = [
            ['reconciled', '=', False],
            ['move_id.state', '=', 'posted'],
        ]
        if start_date:
            base_domain.append(['date', '>=', start_date])
        if end_date:
            base_domain.append(['date', '<=', end_date])
        if customer:
            base_domain.append(['partner_id', 'ilike', customer])

        fields = [
            'date',
            'move_name',
            'ref',
            'name',
            'date_maturity',
            'amount_currency',
            'amount_residual_currency',
            'partner_id',
            'account_id',
            'move_id',
        ]
        # Business filters (as en Odoo UI):
        # - Cuenta 12 o 13, excluyendo 10, 133, 123
        # Build (12% OR 13%) AND NOT 10% AND NOT 133% AND NOT 123%
        # IMPORTANT: domain must be flat (no nested lists), so expand the OR inline
        account_code_or = ['|', ['account_id.code', 'like', '12%'], ['account_id.code', 'like', '13%']]
        excludes = [
            ['account_id.code', 'not ilike', '10%'],
            ['account_id.code', 'not ilike', '133%'],
            ['account_id.code', 'not ilike', '123%'],
        ]

        # Try with account_type (newer versions) + business code filter
        domain_try = base_domain + account_code_or + excludes + [['account_id.account_type', '=', 'asset_receivable']]
        try:
            lines = self.search_read('account.move.line', domain_try, fields, limit=limit)
        except Exception:
            # Try with user_type_id.type (older versions)
            domain_try = base_domain + account_code_or + excludes + [['account_id.user_type_id.type', '=', 'receivable']]
            try:
                lines = self.search_read('account.move.line', domain_try, fields, limit=limit)
            except Exception:
                # Fallback without account type filter (solo por códigos y demás filtros)
                lines = self.search_read('account.move.line', base_domain + account_code_or + excludes, fields, limit=limit)

        # Collect related ids to batch read partners, accounts, moves
        partner_ids = sorted({l['partner_id'][0] for l in lines if isinstance(l.get('partner_id'), list)})
        account_ids = sorted({l['account_id'][0] for l in lines if isinstance(l.get('account_id'), list)})
        move_ids = sorted({l['move_id'][0] for l in lines if isinstance(l.get('move_id'), list)})

        partner_map = {}
        account_map = {}
        move_map = {}

        if partner_ids:
            partner_map = {}
            partner_fields_full = ['vat', 'state_id', 'l10n_pe_district', 'country_id', 'contact_address', 'cod_client_sap']
            try:
                partner_recs = self.models.execute_kw(self.db, self.uid, self.password, 'res.partner', 'read', [partner_ids], {'fields': partner_fields_full})
            except Exception:
                # Fallback without custom fields
                partner_recs = self.models.execute_kw(self.db, self.uid, self.password, 'res.partner', 'read', [partner_ids], {'fields': ['vat', 'state_id', 'l10n_pe_district', 'country_id', 'contact_address']})
            partner_map = {p['id']: p for p in partner_recs}

        if account_ids:
            acc_fields = ['code', 'name']
            acc_recs = self.models.execute_kw(self.db, self.uid, self.password, 'account.account', 'read', [account_ids], {'fields': acc_fields})
            account_map = {a['id']: a for a in acc_recs}

        if move_ids:
            move_map = {}
            try:
                move_fields = ['invoice_origin', 'invoice_user_id', 'sales_channel_id', 'sales_type_id']
                move_recs = self.models.execute_kw(self.db, self.uid, self.password, 'account.move', 'read', [move_ids], {'fields': move_fields})
            except Exception:
                move_recs = self.models.execute_kw(self.db, self.uid, self.password, 'account.move', 'read', [move_ids], {'fields': ['invoice_origin', 'invoice_user_id']})
            move_map = {m['id']: m for m in move_recs}

        # Build rows per requested schema
        rows = []
        for l in lines:
            partner = partner_map.get(l['partner_id'][0]) if isinstance(l.get('partner_id'), list) else {}
            account = account_map.get(l['account_id'][0]) if isinstance(l.get('account_id'), list) else {}
            move = move_map.get(l['move_id'][0]) if isinstance(l.get('move_id'), list) else {}

            def m2o_name(val):
                if isinstance(val, list) and len(val) >= 2:
                    return val[1]
                return ''

            rows.append({
                'date': l.get('date'),
                'I10nn_latam_document_type_id': '',  # Placeholder unless field exists on move/line
                'move_name': l.get('move_name'),
                'invoice_origin': move.get('invoice_origin') or '',
                'account_id/code': account.get('code') or '',
                'account_id/name': account.get('name') or m2o_name(l.get('account_id')),
                'patner_id/cod_client_sap': partner.get('cod_client_sap') or '',
                'patner_id/vat': partner.get('vat') or '',
                'patner_id': m2o_name(l.get('partner_id')),
                'amount_currency': l.get('amount_currency') or 0.0,
                'amount_residual_currency': l.get('amount_residual_currency') or 0.0,
                'date_maturity': l.get('date_maturity'),
                'ref': l.get('ref') or '',
                'name': l.get('name') or '',
                'move_id/invoice_user_id': m2o_name(move.get('invoice_user_id')),
                'patner_id/state_id': m2o_name(partner.get('state_id')),
                'patner_id/l10n_pe_district': partner.get('l10n_pe_district') or '',
                'patner_id/contact_adress': partner.get('contact_address') or '',
                'destiny_adress': '',
                'patner_id/country_code': '',
                'patner_id/country_id': m2o_name(partner.get('country_id')),
                'move_id/sales_channel_id': m2o_name(move.get('sales_channel_id')),
                'move_id/sales_type_id': m2o_name(move.get('sales_type_id')),
            })

        return rows

