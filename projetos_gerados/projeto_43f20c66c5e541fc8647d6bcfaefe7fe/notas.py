def adicionar_nota(notas, nota):
    if isinstance(nota, (int, float)) and not isinstance(nota, bool):
        if nota >= 0:
            if nota <= 10:
                notas.append(nota)
                return True
            else:
                return False
        else:
            return False
    else:
        return False


def calcular_media(notas):
    if not notas:
        return 0.0
    return sum(notas) / len(notas)


def classificar_aluno(media):
    if media >= 0:
        if media <= 10:
            if media >= 7:
                return "Aprovado"
            else:
                if media >= 5:
                    return "Recuperação"
                else:
                    return "Reprovado"
        else:
            return "Média inválida"
    else:
        return "Média inválida"


def avaliar_expressao(expressao):
    return eval(expressao)
