from django import template
from num2words import num2words

register = template.Library()


@register.filter
def currency_to_words(value):
    """
    Converte um valor numérico para texto por extenso em francês
    """
    try:
        if isinstance(value, str):
            value = float(value.replace(',', '.'))

        euros = int(value)
        centavos = int(round((value - euros) * 100))

        euros_text = num2words(euros, lang='fr')

        if centavos > 0:
            centavos_text = num2words(centavos, lang='fr')
            if euros == 1:
                result = f"{euros_text} euro et {centavos_text} centime"
            elif centavos == 1:
                result = f"{euros_text} euros et {centavos_text} centime"
            else:
                result = f"{euros_text} euros et {centavos_text} centimes"
        else:
            if euros == 1:
                result = f"{euros_text} euro"
            else:
                result = f"{euros_text} euros"

        return result.capitalize()

    except (ValueError, TypeError):
        return ""