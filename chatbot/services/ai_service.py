"""
ai_service.py — Chatbot App
---------------------------
Provides explanations of financial results and general financial QA.
This acts as a stub for a real LLM API (like OpenAI), avoiding actual AI computations
for the math (which is handled exactly by the calculator app).
"""

from decimal import Decimal
import re
import os
from django.conf import settings

# Attempt to configure Gemini if key is present
try:
    from google import genai
    from google.genai import types
    if settings.CHATBOT_API_KEY and settings.CHATBOT_API_KEY != 'placeholder-api-key':
        ai_client = genai.Client(api_key=settings.CHATBOT_API_KEY)
        GEMINI_AVAILABLE = True
    else:
        GEMINI_AVAILABLE = False
except ImportError:
    GEMINI_AVAILABLE = False


def explain_result(data: dict, calculation_type: str) -> str:
    """
    Generate a human-readable explanation of a calculation result.
    
    Parameters
    ----------
    data : dict
        The result dictionary from the calculator services.
    calculation_type : str
        'npv', 'irr', 'compound', or 'amortization'
        
    Returns
    -------
    str : A friendly explanation text.
    """
    if calculation_type == "npv":
        npv = data.get("value", Decimal("0"))
        rate = data.get("rate", Decimal("0"))
        if npv > 0:
            return (
                f"El Valor Actual Neto (VAN) es {npv}. Al ser mayor que cero, "
                f"significa que el proyecto generará ganancias por encima de la tasa "
                f"de descuento exigida ({rate*100}%). Es financieramente viable."
            )
        elif npv < 0:
            return (
                f"El Valor Actual Neto (VAN) es {npv}. Al ser menor que cero, "
                f"el proyecto no alcanza a cubrir la tasa de descuento exigida "
                f"({rate*100}%) y destruye valor. No es recomendable."
            )
        else:
            return "El VAN es exactamente cero. El proyecto apenas cubre la tasa exigida."

    elif calculation_type == "irr":
        irr = data.get("value", Decimal("0"))
        percentage = data.get("percentage", Decimal("0"))
        return (
            f"La Tasa Interna de Retorno (TIR) es {irr} ({percentage}%). "
            f"Esta es la tasa de rentabilidad promedio anual que genera la "
            f"inversión. Si esta tasa es mayor que tu costo de capital o "
            f"tasa de descuento, el proyecto es conveniente."
        )

    elif calculation_type == "compound":
        amount = data.get("amount", Decimal("0"))
        interest = data.get("interest_earned", Decimal("0"))
        eff_rate = data.get("effective_rate", Decimal("0"))
        return (
            f"Al final del período, tendrás un total de {amount}. "
            f"De este monto, {interest} corresponden a intereses ganados "
            f"por el efecto de la capitalización compuesta. "
            f"La tasa anual efectiva o real de la inversión fue del {eff_rate * 100}%."
        )

    elif calculation_type == "amortization":
        payment = data.get("payment", Decimal("0"))
        total_int = data.get("total_interest", Decimal("0"))
        return (
            f"Bajo el sistema de amortización francés, pagarás una cuota fija "
            f"constante de {payment} en cada período. "
            f"Al finalizar el plazo, habrás pagado un total de {total_int} "
            f"únicamente en intereses."
        )

    return "No tengo una explicación detallada para este cálculo."


def answer_financial_question(question: str) -> str:
    """
    Answers a financial question using Gemini if configured,
    otherwise falls back to rule-based logic.
    """
    if GEMINI_AVAILABLE:
        try:
            response = ai_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=question,
                config=types.GenerateContentConfig(
                    system_instruction="Eres un asistente financiero y matemático experto. Muestra el procedimiento paso a paso hasta alcanzar el resultado final con alta precisión."
                )
            )
            return response.text.strip()
        except Exception as e:
            # Fallback if API fails
            pass

    q_lower = question.lower()
    
    if "van" in q_lower or "npv" in q_lower or "valor actual neto" in q_lower:
        return (
            "El Valor Actual Neto (VAN) es un indicador financiero que mide la rentabilidad "
            "de un proyecto. Consiste en traer al presente todos los flujos de caja futuros "
            "descontados a una tasa específica y restar la inversión inicial. Si el VAN > 0, el proyecto es viable."
        )
    elif "tir" in q_lower or "irr" in q_lower or "tasa interna" in q_lower:
        return (
            "La Tasa Interna de Retorno (TIR) es la tasa de descuento que hace que el VAN de "
            "un proyecto sea exactamente cero. Es una medida de la rentabilidad del proyecto. "
            "Se acepta un proyecto si su TIR es mayor que la tasa mínima de rentabilidad exigida."
        )
    elif "interés compuesto" in q_lower or "capitalización" in q_lower:
        return (
            "El interés compuesto es aquel que se calcula sobre el capital inicial más los "
            "intereses acumulados de períodos anteriores. A diferencia del interés simple, "
            "los intereses generan más intereses, creando un efecto de 'bola de nieve'."
        )
    elif "amortización" in q_lower or "francés" in q_lower:
        return (
            "El sistema de amortización francés se caracteriza por tener cuotas fijas a lo "
            "largo de todo el préstamo. En las primeras cuotas se paga una gran proporción "
            "de intereses y poco capital, y esta proporción se invierte hacia el final del préstamo."
        )
    elif "hola" in q_lower or "saludos" in q_lower:
        return "¡Hola! Soy tu asistente financiero. Puedo explicarte conceptos como VAN, TIR, interés compuesto o sistemas de amortización. ¿En qué te puedo ayudar?"
    
    return (
        "Como asistente financiero, estoy diseñado para ayudarte a entender conceptos como VAN, "
        "TIR, amortizaciones o interés compuesto. Por favor, sé un poco más específico con tu pregunta financiera."
    )


def parse_user_input(text: str) -> dict:
    """
    Identify user intent.
    Useful for triggering specific UI elements or calculations.
    """
    text = text.lower()
    intent = "general_qa"
    
    if any(kw in text for kw in ["calcula van", "calcular van", "dime el van"]):
        intent = "calculate_npv"
    elif any(kw in text for kw in ["calcula tir", "calcular tir"]):
        intent = "calculate_irr"
        
    return {"intent": intent, "original_text": text}
