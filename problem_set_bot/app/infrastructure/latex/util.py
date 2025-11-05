import os

header = r"""
\documentclass[11pt, luatex]{article}% объявление класса LaTex, размер шроифта, компилятор, две колонки



%------------------------ Разметка страницы --------------------------
\linespread{1.03} %Небольшое увеличение межстрочного расстояния
\usepackage[includeheadfoot, % это означает, что нижнее и верхнее поля отсчитываются от нижнего и верхнего колонтитулов
%showframe,% показывает поля --- нужно для отладки
paperwidth=21.cm, %ширина страницы А4
paperheight=29.7cm, %длина страницы А4
top=1.cm, %верхнее поле
bottom=1.4cm, %нижнее поле
outer=14mm, %внешние поля
inner=14mm, %внутренние поля
marginparwidth=0.6cm, %ширина текста на полях
marginparsep=1.2mm, %расстояние от тела текста до текста на полях
headheight=.5cm,
footskip=1.8cm, %расстояние от нижней границы нижних полей до текста (от нижней основной линии подписи в нижнем колонтитуле до нижней основной линии текста)
columnsep=1cm,
headsep=0.75cm, %расстояние от верхнего колонтитула до текста
heightrounded
]{geometry}

%\geometry{top=20mm}
%\geometry{bottom=20mm}
\geometry{left=11mm}
\geometry{right=11mm}
%-------------------------------------------------------------------------

%--------------- Языковые пакеты, кодировка, переносы ---------------------
\usepackage[]{fontspec}% подключает пакет для работы со шрифтами
\usepackage[english, russian]{babel} % поддержка разных языков
\setromanfont{STIX Two Text} % шрифт roman
\setsansfont{STIX Two Text} % шрифт serif (курсив)
\setmonofont{Anonymous Pro} % моноширный шрифт
\defaultfontfeatures{Ligatures={TeX}} % Лигатуры -- как в обычном TeX
\setmainfont[]{STIX Two Text} % главный шрифт документа

\usepackage[math-style=TeX]{unicode-math} % пакет подключающий нестандартные шрифты для математического режима
\unimathsetup{math-style=TeX} % стиль формул
\setmathfont{texgyrepagella-math.otf} % задаёт шрифт матем.режима
\usepackage[protrusion=true,expansion, shrink=30]{microtype} %нужно, чтобы строки не торчали (улучшает расчёт расстояний между словами в строке)
%---------------------------------------------------------------------------

\usepackage[math-style=TeX]{unicode-math} % пакет подключающий нестандартные шрифты для математического режима
\unimathsetup{math-style=TeX} % стиль формул
\setmathfont{texgyrepagella-math.otf} % задаёт шрифт матем.режима
\usepackage[protrusion=true,expansion, shrink=30]{microtype} %нужно, чтобы строки не торчали (улучшает расчёт расстояний между словами в строке)
%---------------------------------------------------------------------------


\usepackage[framemethod=pstricks]{mdframed}
\usepackage{xcolor}
\usepackage{pstricks}
\usepackage{epsfig}



\usepackage[pstricks]{bclogo} \setlength{\logowidth}{10pt}
\renewcommand\bcStyleTitre[1]{\hskip1.6mm\emph{#1}}


%------------ Форматирование названий раздела \section -------------------
\usepackage{titlesec}
\titlelabel{\thetitle.~}
\titleformat{name=\section}[hang]{\Large}{}{2pt}{\filcenter\thesection.~}{\filcenter}
\titleformat{name=\section,numberless}[hang]% уменьшение расстояния до section
{\Large}%
{}%
{0em}%
{\filcenter}%
\titlespacing{\section}{0pt}{5pt plus 2pt minus 1pt}{0.2\baselineskip}%
%------------------------------------------------------------------------



\usepackage{fontawesome5}
%\usepackage{epstopdf} % Converts EPS to PDF automatically
%\epstopdfsetup{update} % Only regenerate if EPS file changes
\usepackage{graphicx}
\usepackage{fancybox,fancyhdr} %пакет для работы с подписями и линиями в колонтитулах
%\usepackage{eucal,bm, amsthm, amssymb, amsmath, array}
\usepackage[scale=1.18,boondox]{emf} %Символ ЭДС
\usepackage{icomma}

%\DeclareMathOperator{\tg}{tg}
\newcommand{\tgx}{\tg x}

%--------------------------- Подписи к рисункам ---------------------------
\usepackage[hypcap=false]{caption}
\captionsetup[figure]{font={small,sl}, name={К задаче}}
\setlength{\abovecaptionskip}{3pt plus 1pt minus 1pt}
% -------------------------------------------------------------------------
\usepackage{wrapfig}

%------------------------ Номера задач и ответов --------------------------
%\newcounter{zadacha}
%\newcommand{\z}{\par\vspace{5pt plus 1pt minus 1pt}\noindent\addtocounter{zadacha}{1}\hypertarget{z\thezadacha}{}\hyperlink{an\thezadacha}{\psframebox[framearc=.3,linecolor=linkcolor, framesep=1.8pt]{\:\textbf{\arabic{zadacha}}\:}\hskip2mm}}
%\newcounter{answer}
%\newcommand{\an}{\par\vspace{4pt}\noindent\addtocounter{answer}{1}%
	%	\hypertarget{an\theanswer}{}\hyperlink{z\theanswer}{\psframebox[framearc=.3,linecolor=linkcolor, framesep=1.8pt]{\:\textbf{\arabic{answer}}\:}\hskip2mm}}
%--------------------------------------------------------------------------


%---------------------- Определения доп.команд -----------------------------
\newcommand*{\hm}[1]{#1\nobreak\discretionary{}% перенос в формулах по \hm (по Львовскому)
	{\hbox{$\mathsurround=0pt #1$}}{}}
%--------------------------------------------------------------------------


%---------------------- Определения цветов ---------------------------
\definecolor{darkred}{HTML}{8B0000}
\definecolor{linkcolor}{HTML}{120A8F}
%--------------------------------------------------------------------


%---------------------- Гиперссылки ---------------------------
\usepackage[]{hyperref}
\definecolor{violet}{HTML}{800080} % цвет гиперссылок
\hypersetup{linkcolor=myblue	,citecolor=darkred, urlcolor = myblue, colorlinks=true}
\hypersetup{pdfhighlight=/P}
\usepackage[all]{hypcap}
%--------------------------------------------------------------------


%-------------------- Форматирование колонтитулов --------------------
\pagestyle{fancy}
\rhead{\small{\href{https://repetit-fm.ru}{repetit-fm.ru}}}
%	\lhead{\uppercase{\small\textsl{Колебания и волны}}}
%	\chead{\uppercase{\small{Лето, 2023}}}
%\rfoot{\fontspec{Pecita}{Евгений Филипенко}}
\lhead{\uppercase{\small\textsl{Профильная математика}}}
\rhead{\uppercase{\small\textsl{Задачи ФИПИ}}}
%	\lfoot{\href{https://youtube.com}{\includegraphics[height=20pt]{images/youtube-icon.pdf}}}

\lfoot{
	%\href{https://www.youtube.com/@yowfel}{\resizebox{!}{4mm} {\color{red} \faIcon{youtube}}}
	%\hspace*{7mm}
	\href{https://vk.com/club222480852}{\resizebox{!}{4mm}{\color{vkblue} \faIcon{vk}}}
	\hspace*{7mm}
	\href{https://t.me/math_and_beyond}{\resizebox{!}{4.5mm}{\color{myblue} \faIcon{telegram}}} @math\_and\_beyond
} % Requires
\cfoot{\thepage}
\setlength{\textfloatsep}{10pt plus 1.0pt minus 2.0pt}
\setlength{\floatsep}{6pt plus 1.0pt minus 1.0pt}
\setlength{\intextsep}{6pt plus 1.0pt minus 1.0pt}

\makeatletter
% This command ignores the optional argument for itemize and enumerate lists
\newcommand{\inlineitem}[1][]{%
	\ifnum\enit@type=\tw@
	{\descriptionlabel{#1}}
	\hspace{\labelsep}%
	\else
	\ifnum\enit@type=\z@
	\refstepcounter{\@listctr}\fi
	\,\@itemlabel\hspace{\labelsep}%
	\fi}
\makeatother

\usepackage{enumitem}
\setlist{nolistsep}

\AddEnumerateCounter{\asbuk}{\@asbuk}{\cyrm}
\setlist[enumerate,1]{label=\asbuk*),ref=\alph*}
\renewcommand{\theenumii}{\asbuk{enumii}}
\renewcommand{\labelitemi}{---}

\usepackage{answers}
\usepackage{multicol}
\usepackage{multirow}

%\setlength{\parindent}{0.0mm}

\hypersetup{colorlinks=true,linkcolor=myblue}

% solutions file
\Opensolutionfile{mysolutions}
\Newassociation{mysolution}{mySoln}{mysolutions}

% new environment that sets up hypertargets both in the question
% section, and in the answer section
\newlist{myenum}{enumerate}{3}
\newcounter{question}
\newenvironment{question}%
{%
	\refstepcounter{question}%
	%  hyperlink to solution
	\hypertarget{question:{\thequestion}}{}%
	\Writetofile{mysolutions}{\protect\hypertarget{soln:\thequestion}{}}%
	\begin{myenum}[label=\bfseries\protect\hyperlink{soln:\thequestion}{\thequestion.},ref=\thequestion]
		\item%
	}%
	{%
\end{myenum}}

\newcounter{problem}
\newenvironment{problem}[1][]{%
	\refstepcounter{problem}%
	\par\noindent\textcolor{myblue}{\textbf{\theproblem.}}%
	\ \textcolor{myblue}{#1}% Optional title in different color
	\par\noindent\nopagebreak%
}{\par \vspace{2mm}}

\definecolor{myblue}{RGB}{0,82,155}
\definecolor{vkblue}{RGB}{0, 119, 255}
\definecolor{tgblue}{RGB}{39,167,231}
\definecolor{mygreen}{RGB}{0,110,51}
\newcommand{\smallpm}{\mathbin{\raisebox{0.3ex}{$\pm$}}}

\begin{document}

"""

postface = r"""

\newpage
\section*{Послесловие}
Этот файл — часть большого проекта. У нас есть вся база ФИПИ по профильной математике - \textbf{978 отсортированных по темам задач}, файлы по ЕГЭ бесплатны. Для этого нужно вступить в телеграм-канал или в группу
вк, написать в личные сообщения, и мы вам вышлем сборник со всеми задачами. Также файлы с вы можете
получить в нашем телеграм-боте - \href{https://t.me/problem_bank_bot}{@problem\_bank\_bot}, там все задачи по каждой теме, сверстанные в LaTex
– удобные pdf для учителей и учеников, как, например, этот файл. У вас есть возможность поучаствовать и
поддержать работу донатами в группе в контакте и на \href{https://boosty.to/mathandbeyound/donate}{boosty.to}
Ответов к задачам сейчас нет, но есть \textbf{id задачи - ссылка}, по которой можно проверить ответ, если он числовой,
так и сверить условие. Ответы я собираю, поэтому сделал в боте команду, с помощью которой его можно
отправить как текстом, так и фото.
На подходе подборка всей базы ФИПИ по ОГЭ: \textbf{3547 задач, отсортированных по темам»}. Уже сейчас можно
записаться в предзаказ с хорошей скидкой, пока она у нас еще не вышла. Вы получите не только файл, а
возможность получать и его дальнейшие правки и обновления. Уже скоро опубликуем демо версию, следите в
группе или канале.
Следите за обновлениями и качайте подборки.

"""
footer = r"""

	% close solution file
	\Closesolutionfile{mysolutions}

	% renew the solution environment so that it hyperlinks back to
	% the question
	\renewenvironment{mySoln}[1]{%
		% add some glue
		\vskip .5cm plus 2cm minus 0.1cm%
		{\bfseries \hypersetup{linkcolor=mygreen} \hyperlink{question:#1}{#1.}}%
	}%
	{%
	}%
	%\newpage
	%\section*{Ответы}
	\setlength{\parindent}{0.0mm}
	% input the file if it exists
	%\begin{multicols}{2}
	\IfFileExists{mysolutions.tex}{\input{mysolutions.tex}}{}
	%\end{multicols}

\end{document}
"""


async def remove_user_files(user_id, wordir='pdf'):
    tempfiles = [f for f in os.listdir(wordir) if str(user_id) in f]
    for f in tempfiles:
        os.remove(os.path.join('pdf', f))