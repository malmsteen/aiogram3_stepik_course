from jinja2 import Template
import os
from pathlib import Path

OGE_IMG_PATH = "app/infrastructure/latex/images/oge"
INCLUDEGRAPHICS = "\\begin{{center}}\\includegraphics[scale=0.6, valign=m]{{images/{path}}}\\end{{center}}"
MYHREF = "\\myhref{{{href_pref}{source_id}}}{{{source_id}}}"
PROBLEM = "\\begin{{problem}}[{href}]\n{{{text}{fig}}}\n\\end{{problem}}"

subcaption ="""
\\begin{figure}[htbp]
	\centering
	\\begin{subfigure}[c]{0.45\\textwidth}
		\centering
		\includegraphics[scale=0.7]{images/oge/%s}
      	\caption*{рис. 1}
	\end{subfigure}
	\hfill
	\\begin{subfigure}[c]{0.45\\textwidth}
		\centering
		\includegraphics[scale=0.7]{images/oge/%s}
		\caption*{рис. 2}
	\end{subfigure}	
\end{figure}
"""

correspondant = r"""
{{ pre }}
\vspace{2mm}
\begin{center}
\begin{tabular}{lll}
{% if is_reverse %}
    \underline{ГРАФИКИ} \\
    \vspace{2mm}
    \textbf{А)} \includegraphics[scale=0.7, valign=t]{{ figs[0] }} &
    \textbf{Б)} \includegraphics[scale=0.7, valign=t]{{ figs[1] }} &
    \textbf{В)} \includegraphics[scale=0.7, valign=t]{{ figs[2] }} \\
    \\

    \underline{{ subj }} \\
    \vspace{2mm}
    \textbf{1)} {{ conds[0] }} &
    \textbf{2)} {{ conds[1] }} &
    \textbf{3)} {{ conds[2] }} \\
{% else %}
    \underline{{ subj }} \\
    \vspace{2mm}
    \textbf{1)} {{ conds[0] }} &
    \textbf{2)} {{ conds[1] }} &
    \textbf{3)} {{ conds[2] }} \\
    \\
    
    \underline{ГРАФИКИ} \\
    \vspace{2mm}
    \textbf{А)} \includegraphics[scale=0.7, valign=t]{{ figs[0] }} &
    \textbf{Б)} \includegraphics[scale=0.7, valign=t]{{ figs[1] }} &
    \textbf{В)} \includegraphics[scale=0.7, valign=t]{{ figs[2] }} \\
{% endif %}
\end{tabular}
\end{center}

В таблице под каждой буквой укажите соответствующий номер.

\vspace{2mm}
\begin{tabular}{|c|c|c|}\hline
    А & Б & В \\ \hline
    & & \\ \hline
\end{tabular}
"""

include_fig_tmpl = "\includegraphics[scale=0.7, valign=m]{images/oge/%s}"
enum_tmpl = """
\\begin{enumerate}
\\item %s
\\item %s
\\item %s
\\item %s
\\end{enumerate}
"""

enum_tmpl_oge = """
\\begin{enumerate}
{% for item in items %}
\\item {{item}}
{% endfor %}    
\\end{enumerate}
"""

def render_correspondance(problem):   
    
    is_reverse = problem['text'][0] == 'reverse'
    text = problem['text']
    if is_reverse:
        pre = text[1]
        conds = text[2:5]
    else:        
        pre = text[0]
        conds = text[1:4]
        
    if "коэффициент" in ''.join(problem['text']).lower():
        subj = "КОЭФФИЦИЕНТЫ"
    else:
        subj = "ФУНКЦИИ"   
    
    braced_str = lambda x: '{' + str(x) + '}'
    
    figs =[f"images/oge/{problem['source_id']}_{i}" for i in range(1,4)]
    figs_braced = [braced_str(f) for f in figs]

    tmpl = Template(correspondant)
    return tmpl.render(
        pre=pre,
        subj=braced_str(subj),
        figs=figs_braced,
        conds=conds,
        is_reverse=is_reverse)

def find_imgs(prob_id: str) -> int:
    
    path = os.path.join(os.getcwd(), OGE_IMG_PATH)  

    matching_figs = [
        file.name for file in Path(path).iterdir()
        if file.is_file() and file.name[:6].lower() == prob_id.lower()
    ]    
    return matching_figs


def render_single_choiсe(prob):
    source_id = prob['source_id']
    text = prob['text']   
    figs = sorted(find_imgs(source_id))
    # figs = list(filter(lambda f: f.split('.')[0][-1], figs))
    if len(figs) == 0:
        return f"{text[0]}\n" + enum_tmpl % tuple(text[-4:])
    elif len(figs) == 1:
        return (
            f"{text[0]}\n"
            + "\\begin{center}"
            + include_fig_tmpl % tuple(figs)
            + "\\end{center}"
            + f"{text[1] if len(text) > 5 else ''}\n"
            + enum_tmpl % tuple(text[-4:])
        )
    elif len(text) == 2:
        option_num = int(text[-1][0])
        options = []
        for i in range(4):
            if i == option_num:
                options.append(text[1])
            else:
                options.append(include_fig_tmpl % (figs.pop(0)))
        return f"{text[0]}\n" + enum_tmpl % tuple(options)            
    else:
        return f"{text[0]}\n" + enum_tmpl % tuple(include_fig_tmpl % (fig,) for fig in figs)

def render_mult_choiсe(lst) -> str:
    tmpl = Template(enum_tmpl_oge)
    return f"{lst[0]}\n" + tmpl.render(items=lst[1:4]) + f"{lst[-1]}\n"
    


VARIANT_OGE = """\
{header}

\\section*{{Вариант ОГЭ}}

{context_block}

{tasks_1_5}

\\begin{{multicols}}{{2}}
{tasks_6_10}
\\end{{multicols}}

{task_11}

\\begin{{multicols}}{{2}}
{task_12}
{task_13}
{tasks_14_18}
{task_19}
{tasks_20_25}
\\end{{multicols}}

{footer}"""
