import logging

import subprocess
import os
import regex as re
from app.infrastructure.latex.util import footer, header
from aiogram.types.input_file import FSInputFile
import requests

logger = logging.getLogger(__name__)


def send_tex(latex_content, filename, texlive):
    tex_server_url = f"http://{texlive.host}:{texlive.port}/compile"  # IP TeX сервера
    
    response = requests.post(tex_server_url, data=latex_content.encode('utf-8'))
    
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        return True
    else:
        print(f"Error: {response.text}")
        return False


def docker_tex_compile(    
    tex_file: str,
    container: str = 'texlive',
    compiler: str = 'lualatex'
):

    
    # Команда для Docker
    cmd = [
        'docker', 'exec', container,
        compiler, '-interaction=batchmode',        
        tex_file,
       '&&', 'rm', '-f', '*.aux', '*.log', '*.out'        
    ]
    
    # Запуск
    try:
        result = subprocess.run(
            cmd,          
            check=True,
            capture_output=True,
            text=True
        )
        print("Компиляция успешна!")
        print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Ошибка компиляции (код {e.returncode}):")
        print(e.stderr)
        return False

sections = [
    "Планиметрия. Часть I",
    "Векторы",
    "Стереометрия. Часть I",
    "Теория вероятности",
    "",
    "Уравнения. Часть I",
    "Вычисление и преобразование выражений",
    "Применение производной и первообразной",
    "Прикладные задачи",
    "Текстовые задачи",
    "Графики функций",
    "Экстремумы функций",
    "Уравнения",
    "Стереометрия. Часть II",
    "Неравенства",
    "Планиметрия. Часть II",
    "Экономические задачи",    
    "Задачи с параметрами",
    "Задачи по теории чисел",    
]

async def make_pdf(probs, texlive):
    tex_content = ''

    # with open('header.txt','r', encoding='utf-8') as fr:
    #     header = fr.read()
    
    # with open('footer.txt', 'r', encoding='utf-8') as fr:
    #     footer = fr.read()


    
    tex_content += header
    pos = int(probs[0]['position'])-1
    title = sections[pos]
    tex_content += f"\section*{{{title}}}\n\\begin{{multicols}}{{2}}"
    curdir = os.getcwd()
    # print(curdir)
    for prob in probs:               
        
        png = f"app/infrastructure/latex/images/{prob['source_id']}.png"
        fullimgpath = os.path.join(curdir, png)        
        if os.path.exists(fullimgpath):
            fig = "\\begin{center}" + f'\includegraphics[scale=0.6]{{images/{prob['source_id']}}}' + '\end{center}'
        else:
            fig = ""

        text = re.sub('([-+=]+)', r'\\hm{\1}', prob['text'])    
        tex_content +=  f'\n\\begin{{problem}}[{prob['source_id']}]\n{{{text}{fig}}}\n\\end{{problem}}'

    tex_content += footer
    texfile = f'{sections[pos]}.tex'
    pdfpath = f'pdf/{texfile}'
    with open(pdfpath, 'w', encoding='utf-8') as fw:
        fw.write(tex_content)
    
    pdfname = pdfpath.replace('tex','pdf')
    send_tex(tex_content, pdfname, texlive)

    pdf_doc  = FSInputFile(pdfpath.replace('tex','pdf'), filename=f'{title}.pdf')
    return pdf_doc


async def make_pdf_all(probs, texlive):

    tex_content = ''
    tex_content += header
    pos = int(probs[0]['position'])-1
    title = sections[pos]
    tex_content += f"\section*{{{title}}}\n\\begin{{multicols}}{{2}}"
    curdir = os.getcwd()

    j = 0
    for i in range(len(probs)):
        problem = probs[i]
        pos = int(problem['position']) - 1
        if "Решите неравенство" in problem['text']:
            problem['text'] = re.sub("Решите неравенство",'', problem['text'])
            problem['text'] = re.sub('\$(.*?)\$', r'$$\1$$', problem['text'])
            problem['text'] = re.sub('(?<=\$)\.', '', problem['text'])            
        if pos != j:
            j += 1
            action = ''
            title = sections[j]
            if pos == 14:
                action = '\nРешите неравенства'
            tex_content += f"\\end{{multicols}}\n\section*{{{title}}}\n{action}\n\\begin{{multicols}}{{2}}"            

        png = f"app/infrastructure/latex/images/{problem['source_id']}.png"
        fullimgpath = os.path.join(curdir, png)        
        if os.path.exists(fullimgpath):
            fig = "\\begin{center}" + f'\includegraphics[scale=0.6]{{images/{problem['source_id']}}}' + '\end{center}'
        else:
            fig = ""

        text = re.sub('([-+=]+)', r'\\hm{\1}', problem['text'])    
        tex_content +=  f'\n\\begin{{problem}}[{problem['source_id']}]\n{{{text}{fig}}}\n\\end{{problem}}'


    tex_content += footer
    texfile = f'Все типы задач ФИПИ.tex'
    pdfpath = f'pdf/{texfile}'
    with open(pdfpath, 'w', encoding='utf-8') as fw:
        fw.write(tex_content)

    pdfname = pdfpath.replace('tex','pdf')
    send_tex(tex_content, pdfname, texlive)

    pdf_doc  = FSInputFile(pdfpath.replace('tex','pdf'), filename=texfile.replace('tex','pdf'))
    return pdf_doc
    

async def make_problems_pdf(problems, user_id, texlive):
    tex_content = ''
    tex_content += header
    
    title = "Подборка задач"
    tex_content += f"\section*{{{title}}}\n\\begin{{multicols}}{{2}}"
    curdir = os.getcwd()
    # print(curdir)
    for prob in problems:               
        
        png = f"app/infrastructure/latex/images/{prob['source_id']}.png"
        fullimgpath = os.path.join(curdir, png)        
        if os.path.exists(fullimgpath):
            fig = "\\begin{center}" + f'\includegraphics[scale=0.6]{{images/{prob['source_id']}}}' + '\end{center}'
        else:
            fig = ""

        text = re.sub('([-+=]+)', r'\\hm{\1}', prob['text'])    
        tex_content +=  f'\n\\begin{{problem}}[{prob['source_id']}]\n{{{text}{fig}}}\n\\end{{problem}}'

    tex_content += footer
    texfile = f'{title + str(user_id)}.tex'
    texpath = f'pdf/{texfile}'
    pdfpath = texpath.replace('tex','pdf')
    # logger.debug(f"{tex_content}")

    with open(pdfpath, 'w', encoding='utf-8') as fw:
        fw.write(tex_content)
    
    send_tex(tex_content, pdfpath, texlive)

    pdf_doc  = FSInputFile(pdfpath, filename=f'{title}.pdf')
    return pdf_doc