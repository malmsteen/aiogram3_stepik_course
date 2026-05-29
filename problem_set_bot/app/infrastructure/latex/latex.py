import logging

import subprocess
import os
import regex as re
from app.infrastructure.latex.util import footer, footer_oge, header, postface, preface
from aiogram.types.input_file import FSInputFile
from app.infrastructure.latex.templates import render_correspondance, render_single_choiсe, render_mult_choiсe, find_imgs

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


sections = [
    "Планиметрия. Часть I",
    "Векторы",
    "Стереометрия. Часть I",
    "Теория вероятности I",
    "Теория вероятности II",
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
    
    HREF_PREF = texlive.egeurl

    tex_content = header + '\n\n' + preface
    pos = int(probs[0]['position'])-1
    title = sections[pos]
    tex_content += f"\\section*{{{title}}}\n\\begin{{multicols}}{{2}}"
    curdir = os.getcwd()
    # print(curdir)
    for prob in probs:               
        
        png = f"app/infrastructure/latex/images/{prob['source_id']}.png"
        fullimgpath = os.path.join(curdir, png)        
        if os.path.exists(fullimgpath):
            fig = "\\begin{center}" + f'\\includegraphics[scale=0.6]{{images/{prob['source_id']}}}' + '\\end{center}'
        else:
            fig = ""

        text = re.sub('([-+=]+)', r'\\hm{\1}', prob['text'])    
        href = f"\\myhref{{{HREF_PREF + prob['source_id']}}}{{{prob['source_id']}}}"
        tex_content +=  f'\n\\begin{{problem}}[{href}]\n{{{prob['text']}{fig}}}\n\\end{{problem}}'

    tex_content += '\n'+ footer
    texfile = f'{sections[pos]}.tex'
    pdfpath = f'pdf/{texfile}'
    with open(pdfpath, 'w', encoding='utf-8') as fw:
        fw.write(tex_content)
    
    pdfname = pdfpath.replace('tex','pdf')
    send_tex(tex_content, pdfname, texlive)

    pdf_doc  = FSInputFile(pdfpath.replace('tex','pdf'), filename=f'{title}.pdf')
    return pdf_doc


async def make_pdf_all(probs, texlive):

    HREF_PREF = texlive.egeurl

    tex_content = header + '\n\n' + preface
    pos = int(probs[0]['position'])-1
    title = sections[pos]
    tex_content += f"\\section*{{{title}}}\n\\begin{{multicols}}{{2}}"
    curdir = os.getcwd()

    j = 0
    for i in range(len(probs)):
        problem = probs[i]
        pos = int(problem['position']) - 1
        if "Решите неравенство" in problem['text']:
            problem['text'] = re.sub("Решите неравенство",'', problem['text'])
            problem['text'] = re.sub(r'\$(.*?)\$', r'$$\1$$', problem['text'])
            problem['text'] = re.sub(r'(?<=\$)\.', '', problem['text'])            
        if pos != j:
            j += 1
            action = ''
            title = sections[j]
            if pos == 14:
                action = '\nРешите неравенства'
            tex_content += f"\\end{{multicols}}\n\\section*{{{title}}}\n{action}\n\\begin{{multicols}}{{2}}"            

        png = f"app/infrastructure/latex/images/{problem['source_id']}.png"
        fullimgpath = os.path.join(curdir, png)        
        if os.path.exists(fullimgpath):
            fig = "\\begin{center}" + f'\\includegraphics[scale=0.6]{{images/{problem['source_id']}}}' + '\\end{center}'
        else:
            fig = ""

        text = re.sub('([-+=]+)', r'\\hm{\1}', problem['text'])    
        href = f"\\myhref{{{HREF_PREF + problem['source_id']}}}{{{problem['source_id']}}}"
        tex_content +=  f'\n\\begin{{problem}}[{href}]\n{{{problem['text']}{fig}}}\n\\end{{problem}}'


    tex_content += '\n'+ footer
    texfile = f'Все типы задач ФИПИ.tex'
    pdfpath = f'pdf/{texfile}'
    with open(pdfpath, 'w', encoding='utf-8') as fw:
        fw.write(tex_content)

    pdfname = pdfpath.replace('tex','pdf')
    send_tex(tex_content, pdfname, texlive)

    pdf_doc  = FSInputFile(pdfpath.replace('tex','pdf'), filename=texfile.replace('tex','pdf'))
    return pdf_doc
    
async def make_variant(probs, texlive):
    
    HREF_PREF = texlive.egeurl

    tex_content = header + '\n\n' + preface
    title = "Вариант"
    tex_content += f"\\section*{{{title}}}\n\\begin{{multicols}}{{2}}"
    curdir = os.getcwd()
    # print(curdir)
    for prob in probs:               
        
        png = f"app/infrastructure/latex/images/{prob['source_id']}.png"
        fullimgpath = os.path.join(curdir, png)        
        if os.path.exists(fullimgpath):
            fig = "\\begin{center}" + f'\\includegraphics[scale=0.6]{{images/{prob['source_id']}}}' + '\\end{center}'
        else:
            fig = ""

        text = re.sub('([-+=]+)', r'\\hm{\1}', prob['text'])    
        href = f"\\myhref{{{HREF_PREF + prob['source_id']}}}{{{prob['source_id']}}}"
        tex_content +=  f'\n\\begin{{problem}}[{href}]\n{{{prob['text']}{fig}}}\n\\end{{problem}}'

    tex_content += '\n'+ footer
    print(tex_content)
    texfile = f'{title}.tex'
    pdfpath = f'pdf/{texfile}'
    with open(pdfpath, 'w', encoding='utf-8') as fw:
        fw.write(tex_content)
    
    pdfname = pdfpath.replace('tex','pdf')
    send_tex(tex_content, pdfname, texlive)

    pdf_doc  = FSInputFile(pdfpath.replace('tex','pdf'), filename=f'{title}.pdf')
    return pdf_doc

async def make_problems_pdf(problems, user_id, texlive):
   
    HREF_PREF = texlive.egeurl

    tex_content = header    
    title = "Подборка задач"
    tex_content += f"\\section*{{{title}}}\n\\begin{{multicols}}{{2}}"
    curdir = os.getcwd()
    # print(curdir)
    for prob in problems:               
        
        png = f"app/infrastructure/latex/images/{prob['source_id']}.png"
        fullimgpath = os.path.join(curdir, png)        
        if os.path.exists(fullimgpath):
            fig = "\\begin{center}" + f'\\includegraphics[scale=0.6]{{images/{prob['source_id']}}}' + '\\end{center}'
        else:
            fig = ""

        text = re.sub('([-+=]+)', r'\\hm{\1}', prob['text'])    
        href = f"\\myhref{{{HREF_PREF + prob['source_id']}}}{{{prob['source_id']}}}"
        tex_content +=  f'\n\\begin{{problem}}[{href}]\n{{{prob['text']}{fig}}}\n\\end{{problem}}'
    
    tex_content += '\end{multicols}\n' + footer
    texfile = f'{title + str(user_id)}.tex'
    texpath = f'pdf/{texfile}'
    pdfpath = texpath.replace('tex','pdf')
    # logger.debug(f"{tex_content}")

    with open(pdfpath, 'w', encoding='utf-8') as fw:
        fw.write(tex_content)
    
    send_tex(tex_content, pdfpath, texlive)

    pdf_doc  = FSInputFile(pdfpath, filename=f'{title}.pdf')
    return pdf_doc




import os
import re
from .templates import VARIANT_OGE, PROBLEM, INCLUDEGRAPHICS, MYHREF, OGE_IMG_PATH, subcaption


def make_problem(prob, href_pref):
    # print(prob)
    position = prob['position']
    fig = ''
    if position == 1:
        text='\n'.join(prob['text'])        
    elif position in  (7, 13):        
        text = render_single_choiсe(prob)
    elif position == 11:        
        text = render_correspondance(prob)    
    elif position == 19:       
        text = prob['text'][0] if len(prob['text']) == 1 \
            else  render_mult_choiсe(prob['text'])       
    else:
        pngimg = f"{OGE_IMG_PATH}/{prob['source_id']}.png"
        curdir = os.getcwd()
        fig = INCLUDEGRAPHICS.format(path='oge/' + prob['source_id']) \
            if os.path.exists(os.path.join(curdir,pngimg)) else ""
        text = '\n'.join(prob['text'])
    href = MYHREF.format(href_pref=href_pref, source_id=prob['source_id'])
    # print(text)
    return PROBLEM.format(href=href, text=text, fig=fig)


def make_block(probs, href_pref):
    return '\n'.join(make_problem(p, href_pref) for p in probs)




async def make_variant_oge(context, ctx_tasks, rest_tasks, texlive):
    
    href_pref = texlive.ogeurl
    print(rest_tasks)
    by_pos = lambda a, b: [p for p in rest_tasks if a <= p['position'] <= b]
    block = lambda probs: make_block(probs, href_pref) 
    context_imgs = sorted(find_imgs(context['source_id']))
    print(context)
    print(context_imgs)
    if len(context_imgs) == 2:        
        ctx_content = context['content'].replace('img\nimg', subcaption % tuple(context_imgs))
    elif len(context_imgs) == 1:
        ctx_content = context['content'].replace('img', INCLUDEGRAPHICS.format(path='oge/' + context['source_id']))
    else:
        ctx_content = context['content']
    

    tex_content = VARIANT_OGE.format(
        header=header,
        context_block=ctx_content,
        tasks_1_5=block(ctx_tasks),
        tasks_6_10=block(rest_tasks[:5]),
        task_11=make_problem(rest_tasks[5], href_pref=href_pref),
        task_12=block(rest_tasks[6:7]),         
        task_13=make_problem(rest_tasks[7], href_pref=href_pref),
        tasks_14_18=block(rest_tasks[8:13]),
        task_19 = make_problem(rest_tasks[13], href_pref=href_pref),
        tasks_20_25=block(rest_tasks[14:]),
        footer=footer_oge
    )

    print(tex_content)
    texpath = 'pdf/Вариант ОГЭ.tex'
    with open(texpath, 'w', encoding='utf-8') as fw:
        fw.write(tex_content)
    
    send_tex(tex_content, texpath[:-3] + 'pdf', texlive)
    pdf_doc = FSInputFile(texpath[:-3] + 'pdf', filename='Вариант ОГЭ.pdf')
    return pdf_doc