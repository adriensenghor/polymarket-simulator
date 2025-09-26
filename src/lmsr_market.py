# Fichier: src/lmsr_market.py

import math

class LMSRMarket:
    """
    Implémente la logique d'un Market Maker Algorithmique basé sur la 
    Logarithmic Market Scoring Rule (LMSR).

    Les prix des contrats (OUI et NON) sont dérivés de la fonction de coût, 
    qui est une fonction exponentielle des quantités de contrats déjà vendues.
    """
    
    def __init__(self, b: float):
        """
        Initialise le marché de prédiction.

        Args:
            b (float): Le paramètre de liquidité de l'LMSR. 
                       Plus b est élevé, plus le marché est liquide (moins sensible au volume).
        """
        if b <= 0:
            raise ValueError("Le paramètre de liquidité 'b' doit être strictement positif.")
            
        self.b = b
        # Inventaire de contrats vendus par l'AMM
        # qO: Quantité de contrats "OUI" vendus
        # qN: Quantité de contrats "NON" vendus
        self.qO = 0.0
        self.qN = 0.0

    def _cost_function(self, qO: float, qN: float) -> float:
        """
        Calcule le coût total (C) pour l'AMM d'émettre les quantités qO et qN.
        
        Args:
            qO (float): Quantité de contrats OUI.
            qN (float): Quantité de contrats NON.
            
        Returns:
            float: Le coût total, C(qO, qN).
        """
        # Formule de coût LMSR : C(q) = b * ln(sum(exp(qi / b)))
        return self.b * math.log(math.exp(qO / self.b) + math.exp(qN / self.b))

    def get_price(self, outcome: str) -> float:
        """
        Calcule et retourne le prix marginal actuel (probabilité implicite) 
        pour un résultat donné.

        Args:
            outcome (str): Le résultat désiré ("OUI" ou "NON").

        Returns:
            float: Le prix du contrat (entre 0.0 et 1.0).
        """
        if outcome not in ["OUI", "NON"]:
            raise ValueError("Le résultat doit être 'OUI' ou 'NON'.")

        # Calcul de la somme des termes exponentiels (pour éviter de la calculer deux fois)
        sum_exp = math.exp(self.qO / self.b) + math.exp(self.qN / self.b)
        
        # Le prix est le coût marginal (dérivée du coût total)
        # Pi = exp(qi / b) / sum(exp(qj / b))
        if outcome == "OUI":
            price = math.exp(self.qO / self.b) / sum_exp
        else: # "NON"
            price = math.exp(self.qN / self.b) / sum_exp
            
        return price

    def buy_shares(self, outcome: str, quantity: float) -> float:
        """
        Simule l'achat d'une quantité de contrats et met à jour l'inventaire.

        Args:
            outcome (str): Le résultat acheté ("OUI" ou "NON").
            quantity (float): Le nombre de contrats à acheter.

        Returns:
            float: Le coût total payé par l'utilisateur pour cette transaction.
        """
        if quantity <= 0:
            return 0.0

        # 1. Coût total AVANT l'achat (C_initial)
        cost_initial = self._cost_function(self.qO, self.qN)

        # 2. Mise à jour de l'inventaire des quantités
        new_qO = self.qO
        new_qN = self.qN
        
        if outcome == "OUI":
            new_qO += quantity
        elif outcome == "NON":
            new_qN += quantity
        else:
            raise ValueError("Le résultat doit être 'OUI' ou 'NON'.")
            
        # 3. Coût total APRÈS l'achat (C_final)
        cost_final = self._cost_function(new_qO, new_qN)
        
        # 4. Le coût de la transaction est la différence (C_final - C_initial)
        transaction_cost = cost_final - cost_initial
        
        # 5. Mettre à jour l'état interne du marché
        self.qO = new_qO
        self.qN = new_qN
        
        return transaction_cost

    def get_inventory(self) -> tuple[float, float]:
        """Retourne les quantités actuelles des contrats OUI et NON vendus."""
        return self.qO, self.qN

# --- FIN DU FICHIER lmsr_market.py ---