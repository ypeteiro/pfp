"""Presentation helpers for portfolio target settings."""

from decimal import Decimal
from html import escape

from pfp.config import load_target_allocation

LABELS = {
    "EQUITY": "Renta variable",
    "FIXED_INCOME": "Renta fija",
    "GOLD": "Oro",
    "CRYPTO": "Cripto",
}


def targets_html(error: str | None = None, values: dict[str, str] | None = None) -> str:
    configured = load_target_allocation()
    values = values or {key: str(configured.get(key, Decimal("0"))) for key in LABELS}
    rows = "".join(
        f'<label><span>{escape(label)}</span><div class="target-input"><input type="number" name="{key}" min="0" max="100" step="0.01" value="{escape(values.get(key, "0"), quote=True)}"><span>%</span></div></label>'
        for key, label in LABELS.items()
    )
    error_html = f'<div class="form-error">{escape(error)}</div>' if error else ""
    return f'''<h1>Objetivos</h1>
<p class="muted">Define cómo quieres distribuir tu cartera. Estos porcentajes se utilizan en Asignación y Rebalanceo.</p>
<section class="panel targets-panel">{error_html}<form method="post" action="/targets" class="targets-form">
{rows}
<div class="targets-total"><span>Total</span><strong id="targets-total">—</strong></div>
<div class="form-actions"><button type="submit">Guardar objetivos</button><a class="filter-reset" href="/allocation">Cancelar</a></div>
</form></section>
<script>
const inputs = [...document.querySelectorAll('.targets-form input[type="number"]')];
const total = document.getElementById('targets-total');
function updateTotal() {{
  const value = inputs.reduce((sum, input) => sum + (Number(input.value) || 0), 0);
  total.textContent = value.toFixed(2).replace('.', ',') + '%';
  total.className = Math.abs(value - 100) < 0.001 ? 'positive' : 'negative';
}}
inputs.forEach(input => input.addEventListener('input', updateTotal));
updateTotal();
</script>'''
