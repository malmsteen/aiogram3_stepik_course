import subprocess
import os
import regex as re
from app.infrastructure.latex.util import footer, header
from aiogram.types.input_file import FSInputFile


def docker_tex_compile(    
    tex_file: str,
    container: str = 'texlive',
    compiler: str = 'lualatex'
):

    
    # Команда для Docker
    cmd = [
        'docker', 'exec', container,
        compiler, '-interaction=batchmode',        
        tex_file
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

async def make_pdf(probs):
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
        # print(fullimgpath)
        if os.path.exists(fullimgpath):
            fig = "\\begin{center}" + f'\includegraphics[scale=0.6]{{{png}}}' + '\end{center}'
        else:
            fig = ""

        text = re.sub('([-+=]+)', r'\\hm{\1}', prob['text'])    
        tex_content +=  f'\n\\begin{{problem}}[{prob['source_id']}]\n{{\n{text}{fig}\n}}\n\\end{{problem}}'


    tex_content += footer
    texfile = f'{sections[pos]}.tex'
    with open(texfile, 'w', encoding='utf-8') as fw:
        fw.write(tex_content)

    # Пример использования
    docker_tex_compile(    
        tex_file= texfile,
        container='texlive',
        compiler='lualatex'
    )

    pdf_doc  = FSInputFile(texfile.replace('tex','pdf'), filename=f'{title}.pdf')
    return pdf_doc
    