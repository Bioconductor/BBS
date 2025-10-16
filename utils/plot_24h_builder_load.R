### To plot the load of a builder over the span of 24 hours:
###
### 1. Go on the builder and identify the block of 96 lines (4 lines per hour)
###    in uptime.log that correspond to the 24 hours window that you want to
###    plot. First line in the block should be for time 00:00:01 and last time
###    in the block should be for time 23:45:01.
###
### 2. Copy/paste the 96 lines into a local file on your laptop. Let's call
###    this file uptime24.txt.
###
### 3. Run the following command in a terminal:
###
###     cat uptime24.txt | cut -d ',' -f 1,4 | cut -d ' ' -f 2,9 >uptime.txt
###
###    This only keeps the 2 columns we need for the plot.
###
### 4. From R, generate the plot with:

library(ggplot2)

df <- read.table("uptime.txt")
colnames(df) <- c("time", "load")

myplot <- ggplot(df, aes(x=time, y=load)) +
          geom_bar(stat="identity", fill="steelblue") +
          theme(axis.text.x=element_text(angle=90, vjust=0.5))
myplot

ggsave("nebbiolo2_24h_load.png", plot=myplot, width=12, height=8, units="in", dpi=300)

