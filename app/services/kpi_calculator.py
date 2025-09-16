from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List, Tuple


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        # Odoo dates are usually 'YYYY-MM-DD'
        return datetime.strptime(value, "%Y-%m-%d").date()
    except Exception:
        return None


def compute_kpis(invoices: List[Dict]) -> Dict[str, float]:
    today = date.today()
    total_invoices = len(invoices)
    overdue_amount = 0.0
    not_due_amount = 0.0
    total_overdue_days = 0
    overdue_count = 0

    for inv in invoices:
        residual = float(inv.get("amount_residual") or 0.0)
        due_date = _parse_date(inv.get("invoice_date_due"))
        if residual <= 0:
            continue
        if due_date and due_date < today:
            overdue_amount += residual
            overdue_days = (today - due_date).days
            if overdue_days > 0:
                total_overdue_days += overdue_days
                overdue_count += 1
        else:
            not_due_amount += residual

    avg_overdue_days = (total_overdue_days / overdue_count) if overdue_count else 0.0

    return {
        "total_facturas": total_invoices,
        "monto_vencido": round(overdue_amount, 2),
        "monto_vigente": round(not_due_amount, 2),
        "promedio_dias_morosidad": round(avg_overdue_days, 2),
    }


def top15_clients(invoices: List[Dict]) -> Tuple[List[str], List[float]]:
    by_partner: Dict[str, float] = {}
    for inv in invoices:
        residual = float(inv.get("amount_residual") or 0.0)
        if residual <= 0:
            continue
        partner = inv.get("partner_id")
        # partner_id can be [id, name] per xmlrpc search_read
        partner_name = None
        if isinstance(partner, list) and len(partner) >= 2:
            partner_name = str(partner[1])
        elif isinstance(partner, str):
            partner_name = partner
        else:
            partner_name = "(Sin nombre)"
        by_partner[partner_name] = by_partner.get(partner_name, 0.0) + residual

    # Sort and take top 15
    sorted_items = sorted(by_partner.items(), key=lambda x: x[1], reverse=True)[:15]
    clientes = [name for name, _ in sorted_items]
    montos = [round(amount, 2) for _, amount in sorted_items]
    return clientes, montos


