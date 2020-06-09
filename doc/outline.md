# Thesis document outline

1. Introduction
2. State of the art
   1. Tokenization
      1. Tokenization methods
      2. BPE
      3. BPE dropout
   2. Translation
      1. NMT? open vocabulary problems?
3. Development
   1. Coding practices
   2. Implementation of BPE
      1. Learn BPEs
      2. Apply BPEs
      3. Align BPEs
      4. Calculate BPE scores
   3. Implementation of BPE dropout
   4. Implementation of BPE dropout on source or target side
   5. Improvement over BPE dropout
   6. ...
4. ...
5. Future work
6. Conclusion

## tasks

* [X] summary of my learn_bpe vs. paper learn_bpe, differences, is this paper material? track algorithm performance in my computer, write in percentage. this algo is 1.4% faster than X.

## bpe dropout

* with dropout is getting worse, check bpe dropout paper again how they do it
  * They produce multiple segmentations
  * During segmentation, at each merge step some merges are randomly dropped with probability p
  * using BPE-Dropout on the source side is more beneficial than using it on the target side
  * The improvement with respect to normal BPE are consistent no matter the vocabulary size. But the effect from using BPE-Dropout vanishes when a corpora size gets bigger.

## scores

* In normal mode, BPE vs. gold standard
* In dropout mode, dropout BPE vs. BPE

* bpe_dropout paper has highest score at dropout=0.1, dropout_iterations=10, merge_threshold=0.7 with f1=0.666
* my tests have highest score at dropout=0.3, dropout_iterations=30, merge_threshold=0.5 with f1=0.685
* same result at dropout=0.2, dropout_iterations=30, merge_threshold=0.5 with f1=0.684
* for dropout=0.1, no difference between dropout_iterations=10 or 30

## no_space learn_bpe results

* space: 0.49/0:54/0:56/1:52 eng, 1:19/1:16/1:28/2:36 deu
* no_space: 4/6:13 eng, 4:25/4:50 deu

## latex cheatsheet

```latex

\chapter{Checklists}

\section{Language}
\label{sec:structure}

standards~\cite{hering:technical_reports,grossman:chicago_manual}
text~\cite{ieee:citation}.

~\ref{sec:appendix} on page~\pageref{sec:appendix}.

for acronyms:  \acs{ISO}

\bigskip

\begin{labeling}{TeXnicCenter:~}
  \item[MiKTeX:] from \url{http://www.miktex.org/} as a LaTeX back end (don't use the 64-bit version, problems with \textsf{biber})
 \item[SumatraPDF:] from \url{http://blog.kowalczyk.info/software/sumatrapdf/} as a PDF viewer
  \item[TeXnicCenter:] from \url{http://www.texniccenter.org/} as a LaTeX front end
  \item[JabRef:] from \url{http://jabref.sourceforge.net/} as a BibTeX editor
  \item[TortoiseSVN:] from \url{http://tortoisesvn.net/} for version control
  \item[XnView:] from \url{http://www.xnview.com/de/} for photo editing
\end{labeling}

\begin{itemize}
   \item[$\Box$] for checkbox
\end{itemize}
\begin{enumerate}
   \item[$\Box$] for checkbox
\end{enumerate}

\begin{table}
  \caption{Page margins that have to be observed in the preparation of degree theses.}
  \label{tab:margins}
  \centering
    \begin{tabular}{lS}
      \toprule
      Position    & {Margin (\si{\centi\meter})} \\
      \midrule
      left        &   2.5 \\
      right       &   2.5 \\
      top       	&   2.5 \\
      bottom      &   2.0 \\
      \bottomrule
    \end{tabular}
\end{table}
```
