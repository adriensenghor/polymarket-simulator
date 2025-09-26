# Fichier: main.py

# ASSUREZ-VOUS D'AVOIR CRÉÉ LE FICHIER ET LA CLASSE LMSRMarket dans src/
from src.lmsr_market import LMSRMarket
import matplotlib.pyplot as plt
import gradio as gr
import math # Ajouté pour les calculs d'injection de biais
from typing import Dict, Any

# --- Gestion de l'état du marché ---
# L'état est stocké ici pour être persistant entre les appels Gradio.
market_state: Dict[str, Any] = {
    "market": None,
    "price_history": [],
    "trade_count": 0
}

# --- Fonctions utilitaires pour le graphique (Simplifiée) ---

def plot_price_history(price_history):
    """Génère le graphique de l'historique des prix OUI et retourne l'objet Figure."""
    
    # Utilisez plt.figure pour créer une nouvelle figure à chaque appel
    fig, ax = plt.subplots(figsize=(8, 4)) 
    
    trade_indices = list(range(len(price_history)))
    
    ax.plot(trade_indices, price_history, label="Prix OUI", color='blue', marker='o', markersize=3, linestyle='-')
    ax.axhline(0.5, color='gray', linestyle='--', linewidth=1, label="Initial (50%)")
    
    ax.set_title("Évolution du Prix du Contrat 'OUI'")
    ax.set_xlabel("Numéro du Trade")
    ax.set_ylabel("Probabilité / Prix")
    ax.set_ylim(0, 1)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Retourne la figure Matplotlib. Gradio (gr.Plot) sait comment l'afficher.
    return fig


# --- Fonctions d'interface Gradio ---

def setup_market(b_value: float, initial_price_oui: float):
    """Ouvre le marché avec une valeur de b donnée et applique le biais initial."""
    global market_state
    
    if not (0.01 <= initial_price_oui <= 0.99):
        return (f"❌ Erreur: Le prix initial doit être entre 0.01 et 0.99.", 0.0, None, 
                gr.update(interactive=False), gr.update(interactive=False), "N/A")

    try:
        # 1. Créer la nouvelle instance du marché avec b
        market = LMSRMarket(b=b_value)
        
        # 2. Appliquer le biais initial (injection de contrats)
        # On calcule combien de contrats (injection_amount) il faudrait injecter 
        # pour obtenir le prix P souhaité dans l'AMM LMSR.
        # Pour LMSR, P_O = exp(q_O/b) / (exp(q_O/b) + exp(q_N/b)).
        # Si on veut un prix P_O, on doit avoir q_O / b - q_N / b = ln(P_O / (1 - P_O)).
        # Pour une injection initiale simple (q_N = 0), on a :
        injection_amount = b_value * math.log(initial_price_oui / (1 - initial_price_oui))
        
        if injection_amount > 0:
            # Injecter des contrats OUI
            market.qO = injection_amount
            market.qN = 0.0 # Initialisation implicite
            
        elif injection_amount < 0:
            # Injecter des contrats NON (injection_amount est négatif, on l'inverse)
            market.qO = 0.0
            market.qN = abs(injection_amount)
            
        # Mettre à jour l'état global
        market_state["market"] = market
        market_state["trade_count"] = 0
        market_state["price_history"] = [initial_price_oui]
        
        # 3. Préparer les sorties
        market_price = market.get_price("OUI")
        graph_fig = plot_price_history(market_state["price_history"])
        qO, qN = market.get_inventory()
        initial_trade_inventory = f"OUI: {qO:.0f} | NON: {qN:.0f}"
        
        initial_message = (
            f"✅ Marché Ouvert ! (b={b_value})\n"
            f"Prix OUI initial (biaisé): {market_price:.4f}"
        )
        
        # Activation des boutons et retour des données
        return (initial_message, market_price, graph_fig, 
                gr.update(interactive=True), gr.update(interactive=True), 
                initial_trade_inventory)
        
    except ValueError as e:
        return (f"❌ Erreur lors de l'initialisation: {e}", 0.0, None, 
                gr.update(interactive=False), gr.update(interactive=False), 
                "N/A")


def execute_trade(outcome: str, quantity: float):
    """Exécute l'achat de contrats et met à jour l'état du marché."""
    global market_state
    market: LMSRMarket = market_state["market"]
    
    # Vérification d'état
    if market is None:
        return "❌ Veuillez d'abord ouvrir le marché.", 0.0, None, "N/A", "N/A"

    if quantity <= 0:
        return "⚠️ La quantité doit être > 0.", market.get_price("OUI"), None, "N/A", "N/A"

    # 1. Exécuter le trade
    cost = market.buy_shares(outcome, quantity)
    
    # 2. Mettre à jour l'historique et le compteur
    market_state["trade_count"] += 1
    new_price_oui = market.get_price("OUI")
    market_state["price_history"].append(new_price_oui)
    
    # 3. Générer le nouveau graphique
    graph_fig = plot_price_history(market_state["price_history"])

    # 4. Préparer les messages de retour
    qO, qN = market.get_inventory()
    
    update_message = (
        f"Trade #{market_state['trade_count']}: Achat de {quantity:.0f} '{outcome}' effectué.\n"
        f"Coût de la transaction: {cost:.2f}$.\n"
        f"Nouveau Prix OUI: {new_price_oui:.4f}"
    )
    
    inventory_str_total = f"AMM: OUI {qO:.0f} | NON {qN:.0f}"
    trade_inventory_str = f"OUI: {qO:.0f} | NON: {qN:.0f}"
    
    return update_message, new_price_oui, graph_fig, inventory_str_total, trade_inventory_str

# --- Définition de l'interface Gradio ---

with gr.Blocks(title="LMSR Polymarket Simulator") as demo:
    gr.Markdown("# 📉 Simulateur de Marché de Prédiction (LMSR) avec Biais")
    gr.Markdown("Définissez la liquidité (**b**) et le **Prix Initial OUI** pour ouvrir le marché, puis tradez.")

    # Section 1: Configuration du marché
    with gr.Row():
        b_input = gr.Slider(minimum=1, maximum=200, value=10, label="Paramètre de Liquidité (b)", step=10)
        # NOUVEAU : Input pour le biais initial
        initial_price_input = gr.Slider(minimum=0.01, maximum=0.99, value=0.50, label="Prix Initial OUI (Biais)", step=0.01)
        open_btn = gr.Button("Ouvrir/Réinitialiser le Marché 🔄", variant="primary")
        
    market_status = gr.Textbox(label="Statut du Marché", value="Veuillez définir 'b' et cliquer sur 'Ouvrir'.")
    
    # Section 2: État actuel du marché
    with gr.Row():
        current_price = gr.Number(label="Prix actuel du contrat OUI", value=0.5, interactive=False)
        inventory_display = gr.Textbox(label="Inventaire AMM Total", value="N/A", interactive=False) 

    # Section 3: Interface de Trading
    gr.Markdown("---")
    gr.Markdown("### Exécuter un Trade")
    
    with gr.Row():
        trade_quantity = gr.Slider(minimum=1, maximum=10, value=2, label="Quantité de Contrats [1-10]", step=1)
        
        # AFFICHAGE DE L'INVENTAIRE DES TRADES (au même niveau que les boutons)
        trade_inventory_display = gr.Textbox(
            label="Contrats Échangés", 
            value="N/A", 
            interactive=False, 
            scale=1
        )
        
    with gr.Row():
        buy_oui_btn = gr.Button("Acheter Contrats OUI", variant="secondary", interactive=False)
        buy_non_btn = gr.Button("Acheter Contrats NON", variant="secondary", interactive=False)
        
    trade_log = gr.Textbox(label="Journal des Trades")

    # Section 4: Visualisation
    gr.Markdown("### Évolution du Prix")
    price_plot = gr.Plot(label="Graphique des Prix")

    # --- Connexions (Flux de Données) ---

    # 1. Ouvrir le marché (AJOUT DE L'INPUT initial_price_input)
    open_btn.click(
        setup_market,
        inputs=[b_input, initial_price_input],
        outputs=[market_status, current_price, price_plot, buy_oui_btn, buy_non_btn, trade_inventory_display]
    )

    # 2. Exécuter le trade OUI
    buy_oui_btn.click(
        execute_trade,
        inputs=[gr.State("OUI"), trade_quantity], 
        outputs=[trade_log, current_price, price_plot, inventory_display, trade_inventory_display]
    )

    # 3. Exécuter le trade NON
    buy_non_btn.click(
        execute_trade,
        inputs=[gr.State("NON"), trade_quantity],
        outputs=[trade_log, current_price, price_plot, inventory_display, trade_inventory_display]
    )

# Lancer l'application Gradio
if __name__ == "__main__":
    demo.launch()