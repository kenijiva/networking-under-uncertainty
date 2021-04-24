set terminal pdfcairo dashed font "Gill Sans,10" linewidth 2 rounded fontscale 1.0

# Line style for axes
set style line 80 lt rgb "#808080"

# Line style for grid
set style line 81 lt 0  # dashed
set style line 81 lt rgb "#808080"  # grey
# set missing "?"

set grid back linestyle 81
set border 3 back linestyle 80 # Remove border on top and right.  These
             # borders are useless and make it harder
                          # to see plotted lines near the border.
                              # Also, put it in grey; no need for so much emphasis on a border.
                              set xtics nomirror
                              set ytics nomirror

#set output "output/variance.pdf"
set output "cost_over_edges.pdf"
#set format y "%e"
set ylabel "Cost [Mil. $]" font ",9" offset 1.5
set xlabel "Number of constructed links" font ",9" offset 2
#set format y "%.2f"
#set ylabel sprintf("Ω [10^%d rpm]", Power) enhanced

unset key
#unset key
#set key top right outside
#set key inside bottom right font ",8"
#set key above font ",7" horizontal
#set key spacing 1.5 samplen 0.5 height 0.7
#unset key
#set format y "%.8f"
#set format y "10^{%L}"

set xtics font ",9" 0,1,3
set ytics font ",9" #0,1,3

#set yrange[0:]
#set xrange[1:2.1]
set xrange [0:3]
set yrange[0:70]
#
#plot "cost_over_edges.dat" using 1:2 smooth cspline lc rgb "red" lw 1.5 lt 2
plot "cost_over_edges.dat" using 1:($2/1000000) w linespoints lw 1.5 lt 2 lc rgb "#CC6677"

#plot "test.txt" using 1:2 title 'Column', "test.txt" using 1:2 smooth cspline lc rgb "red" lw 1.5 lt 2
