import os

from notas import adicionar_nota, calcular_media, classificar_aluno


def main():
    notas = []
    for nota in [8.0, 6.5, 7.5, 9.0]:
        adicionar_nota(notas, nota)

    media = calcular_media(notas)
    situacao = classificar_aluno(media)

    print("Notas:", notas)
    print("Média:", media)
    print("Situação:", situacao)


if __name__ == "__main__":
    main()
