import plotly.graph_objects as go
import plotly.express as px

def format_inr(amount):
    """Formats float amount to Indian Rupee currency format (₹)."""
    if amount is None or amount != amount:
        return "₹0"
    amount = float(amount)
    if amount >= 10_00_000:
        return f"₹{amount / 10_00_000:.2f} L"
    elif amount >= 1_000:
        return f"₹{amount / 1_000:.1f} K"
    else:
        return f"₹{amount:,.0f}"

def generate_sku_explanation(sku_row):
    """
    Dynamically generates natural-language business explanation for why a SKU
    received a specific risk classification.
    """
    action = sku_row['recommended_action']
    lead_demand = sku_row['lead_time_demand']
    on_hand = sku_row['on_hand_units']
    on_order = sku_row['on_order_units']
    available = on_hand + on_order
    rev_risk = sku_row['revenue_at_risk']
    cap_locked = sku_row['capital_locked']
    lead_days = sku_row['lead_time_days']
    forecast_8w = sku_row['forecast_8w_demand']
    overstock_ratio = sku_row['overstock_ratio']

    if action == 'REORDER NOW':
        return (
            f"Projected demand during the {lead_days}-day replenishment lead time is {lead_demand:.0f} units, "
            f"which exceeds total available stock ({available:.0f} units = {on_hand:.0f} on hand + {on_order:.0f} on order). "
            f"This creates an elevated stockout risk with estimated {format_inr(rev_risk)} in unfulfilled sales revenue at stake. "
            f"Action: Raise a purchase order immediately to avoid stockout."
        )
    elif action == 'MARKDOWN / CLEAR':
        return (
            f"Current on-hand inventory ({on_hand:.0f} units) is {overstock_ratio:.1f}x higher than total predicted 8-week demand ({forecast_8w:.0f} units). "
            f"This ties up approximately {format_inr(cap_locked)} in working capital that risks obsolescence. "
            f"Action: Consider promotional markdowns or bundled sales to liquidate excess stock."
        )
    elif action == 'INVESTIGATE':
        return (
            f"SKU displays erratic demand patterns alongside simultaneous high stockout risk and high pipeline stock "
            f"({on_order:.0f} units on order vs {on_hand:.0f} units on hand). "
            f"Action: Manual operations review required to adjust lead time or reorder batch sizes."
        )
    else: # HEALTHY
        return (
            f"Inventory position ({on_hand:.0f} units on hand, {on_order:.0f} on order) safely matches expected demand ({lead_demand:.0f} units over lead time) "
            f"without incurring excess capital lockup. "
            f"Action: Maintain standard replenishment monitoring."
        )

# Corporate Dark / Clean Palette for Analytics Dashboard
COLOR_PALETTE = {
    'primary': '#6366F1',     # Indigo
    'secondary': '#3B82F6',   # Blue
    'success': '#10B981',     # Emerald / Healthy
    'warning': '#F59E0B',     # Amber / Medium Risk / Markdown
    'danger': '#EF4444',      # Red / Stockout / Critical
    'dark': '#1F2937',        # Slate Gray
    'card_bg': '#1E293B',
    'text': '#F8FAFC'
}
