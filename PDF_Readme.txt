This tool enlarges PDF "hairlines" to a readible (and printable) size.  Technically, this is a problem with the .PDF file, and should be corrected by the document creator.  This tool exists in case they cannot (or will not) fix it.  Note that modifying a copyrighted .PDF may be illegal; use your judgement.

For example, a typical PDF may have a drawing which is too thin to view well and doesn't print at all.  When this tool is run on it, the thin lines are identified as 0.013pt.  You set these to be 0.6pt, and they then look and print fine.  If still too thin, try 1 or 2pt; some experimentation is needed.

To get this tool working, first make sure you have Python v3.5 or greater installed.  Get it from https://www.python.org/downloads/.  OLDER VERSIONS OF PYTHON WILL NOT WORK.  v3.12 works.  It also needs GhostScript; get that from: https://www.ghostscript.com/download/gsdnld.html or from your Linux repo.  * Since GS may not default to installing into the PATH on Windows, either move it into the PATH, or move it alongside these files so no path is needed.

For Windows, try to run the PDF_Fix.py file by double-clicking on it.  A cmd window should appear and display usage info.  If instead a message is displayed about needing ghostscript, then get that and try again.  Once double-clicking the .py file just shows the usage, then you are ready to begin conversions.  Just find a PDF file to convert, and drag-and-drop it onto PDF_FixHairLines.cmd.  

In linux, use the .sh file in terminal, ala ./PDF_FixHairlines.sh ~/Downloads/PDF_FixHairLines/Test.pdf.  A sample .pdf is included with thin lines, both before and after "fixing."  Note, many modern PDF readers will render these thin lines to the screen just fine - printing them however is another story.

How this works: this tool first uncompresses the .pdf file.  Then it searches through the uncompressed version for thin line weights.  Any thin lines (under 1.0pt) found are reported and can be changed.  The result is recompressed and saved with "-fixed" appended to it's filename.  The original file is not modified.  The intermediate, uncompressed file is removed.

NOTE this tool is rather "hack-ish" and may not work at all.  It may have unforeseen bugs, especially as Python evolves, and could potentially bork your PDF's.  Always work on copies, not the original files.

RDTSC/2021
