"""
09/04/2022

Projeto 2 - Teoria e Aplicação de Grafos - 2021.2

Universidade de Brasília - Instituto de Ciências Exatas - Departamento de Ciência da Computação (CiC)

Professor: Díbio Leandro Borges

Considere para efeito deste projeto que uma determinada universidade oferece anualmente uma lista de
trinta (30) projetos financiados e abertos a participação de alunos. Cada projeto é orientado e
gerenciado por professores que estabelecem as quantidades mínima e máxima de alunos que podem ser
aceitos em determinado projeto, bem como requisitos de histórico e tempo disponível que os alunos
devem possuir para serem aceitos. Esses requisitos de histórico e tempo são pré-avaliados e cada aluno
possui uma Nota agregada inteira de [3, 4, 5], sendo 3 indicando suficiente, 4 boa, e 5 excelente. Neste
ano cem (100) alunos se candidataram aos projetos. O ideal é que o máximo de projetos sejam
realizados, mas somente se o máximo de alunos qualificados tenham tido o interesse para tal. Para uma
seleção impessoal e competitiva um algoritmo que realize um emparelhamento estável máximo deve
ser implementado. Este projeto pede a elaboração, implementação e testes com a solução final de
emparelhamento máximo estável para os dados fornecidos. Os alunos podem indicar no máximo três
(3) preferências em ordem dos projetos. Variações do algoritmo Gale-Shapley devem ser usadas, com
uma descrição textual no arquivo README do projeto indicando qual variação/lógica foi
utilizada/proposta. O programa deve tentar, e mostrar todas na tela, dez (10) iterações de
emparelhamento em laço, organizando as saídas até a alocação final. Os pares Projetos x Alunos finais
devem ser indicados, bem como os números finais. As soluções dadas em (Abraham, Irving & Manlove,
2007) são úteis e qualquer uma pode ser implementada com variações pertinentes. Um arquivo
entradaProj2TAG.txt com as indicações de código do projeto, número de vagas, requisito mínimo das
vagas, bem como dos alunos com suas preferências de projetos na ordem e suas notas indviduais, é
fornecido como entrada. Uma versão pública do artigo de (Abraham, Irving & Manlove, 2007) é
fornecida para leitura.
"""
import re
def get_graph_from_file(file_name):
    """
    A função monta o grafo a partir do arquivo input. Retorna um dicionário que representa os projetos, e um que representa os estudantes.
    """
    projects = {}
    students = {}
    with open(file_name) as file:
        for line in file:
            if line.startswith('('):
                line = list(map(int, re.findall("\d+", line)))
                if len(line) == 3:
                    projects[line[0]] = {'slots': [-1] * line[1], 'preferences': list(range(5, line[2]-1, -1))}
                else:
                    students[line[0]] = {'preferences': line[1:-1], 'next_pref': 0, 'grade': line[-1], 'curr_proj': -1}
    return projects, students



def try_insert_student(projects, students, current_student_id):
    """
    Esta função tenta inserir o aluno em algum de seus projetos, em ordem de preferência.
    Ela checa se todos os projetos já foram tentados, e se não, verifica se o aluno possui nota.
    Caso possua, ela checa se o projeto possui uma vaga livre e o insere. 
    Caso não, ela compara as notas dos alunos atuais, e caso a nota do aluno seja maior, substitui o aluno de menor nota.
    Retorna o id do aluno a ser reinserido na fila, ou seja, tanto do aluno que foi retirado quando do aluno que está para ser inserido, caso a inserção falhe.
    No caso em que todas as possibilidades de projeto do aluno foram testadas, ou que o aluno foi inserido com sucesso em uma vaga que estava livre, é retornado -1 (flag para evitar a reinserção).
    """
    current_student = students[current_student_id]
    next_pref_id = current_student['next_pref']
    current_student['next_pref'] += 1

    if (next_pref_id == len(current_student['preferences'])):
        return -1
    
    next_pref = current_student['preferences'][next_pref_id]
    current_project = projects[next_pref]
    grade = current_student['grade']
    if (grade in current_project['preferences']):
        slots = current_project['slots']
        if (-1 in slots):
            slots[slots.index(-1)] = current_student_id
            current_student['curr_proj'] = next_pref
            return -1
        else:
            students_proj = list(map(lambda a_id: (a_id, students[a_id]), slots))
            grades_students = list(map(lambda a: (a[0], a[1]['grade']), students_proj))
            grade_min = min(list(map(lambda n: n[1], grades_students)))
            if (grade > grade_min):
                out_student_id = next(filter(lambda n: n[1] == grade_min, grades_students))[0]
                slots[slots.index(out_student_id)] = current_student_id
                students[out_student_id]['curr_proj'] = -1
                current_student['curr_proj'] = next_pref
                return out_student_id

    return current_student_id



def beautify_projs(projects):
    """
    A função irá iterar pelo estado atual dos projetos, e printar, para cada um, os alunos atuais.
    """
    for p in projects:
        curr_proj = projects[p]
        slots = curr_proj['slots']
        if (max(slots) != -1):
            print(f"  - Projeto {p} possui alunos: ", end='')
            print(*[s for s in slots if s != -1])
        else:
            print(f"  - Projeto {p} não possui alunos")



def gale_shapley(projects, students):
    """
    A função executa o algoritimo de Gale Shapley, que resolve o problema do emparelhamento estável. 
    Foi utilizada a variante padrão do Gale-Shapley, encontrada nos slides fornecidos durante a aula. 
    Portanto, para a decisão de empate, o algorítmo vai dar prioridade para o aluno em que seu id vem primeiro, pois dessa forma, o algorítmo, ao comparar as notas, considera que o aluno que veio depois não possui nota maior (afinal, houve empate), e portanto, ele é desconsiderado.
    Obtemos uma fila de alunos livres e vamos tentando alocar cada aluno em seus projetos, de acordo com suas preferências e vagas disponíveis.
    O algoritimo utiliza uma fila, que irá conter todos os alunos livres e que ainda possuem possibilidades de projeto para entrar.
    É executado um loop while, onde é tentado alocar o aluno. Ele roda até a lista ficar vazia.
    Para fins de análise, o estado atual da iteração será printada 10x durante o percorrimento do algorítmo.
    """
    students_queue = [s for s in students if students[s]['curr_proj'] == -1]
    counter, prints_counter = 1, 1
    while students_queue:
        current = students_queue.pop(0)
        out_id = try_insert_student(projects, students, current)
        if out_id != -1:
            students_queue.append(out_id)
        if (counter % 29 == 0):
            print(f"Printando, pela {prints_counter}a vez. {counter}a iteração:")
            beautify_projs(projects)
            prints_counter += 1
        counter += 1



if __name__ == "__main__":
    projects, students = get_graph_from_file('entradaProj2TAG.txt')
    gale_shapley(projects, students)
    print("Printando, pela última vez. Locação final:")
    beautify_projs(projects)