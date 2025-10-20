### To plot the load of a builder over the span of 24 hours:
###
### 1. Go on the builder and identify the block of 96 lines (4 lines per hour)
###    in uptime.log that correspond to the 24-hour window that you want to
###    plot. First line in the block should be for time 00:00:01 and last time
###    in the block should be for time 23:45:01.
###
### 2. Copy/paste the 96 lines into a local file on your laptop. Let's call
###    this file uptime-YYYYMMDD.log (replace YYYYMMDD with the date that
###    corresponds to the 24-hour window).
###
### 3. From R, generate the plot with:

library(ggplot2)

read_uptime24_log <- function(uptime24_log)
{
    lines <- readLines(uptime24_log)
    stopifnot(length(lines) == 96L)
    ## Extract loads.
    loads <- sub(".*load average: ", "", lines)
    loads <- strsplit(loads, ",", fixed=TRUE)
    m <- matrix(as.numeric(unlist(loads)), ncol=3L, byrow=TRUE)
    loads <- m[ , 1L]
    ## Extract times.
    times <- trimws(sub(":[0-9]* up .*$", "", lines))
    stopifnot(times[[1L]] == "00:00", times[[96L]] == "23:45")
    data.frame(time=times, load=loads)
}

plot_24h_load <- function(uptime24_log)
{
    df <- read_uptime24_log(uptime24_log)
    ggplot(df, aes(x=time, y=load)) +
        geom_bar(stat="identity", fill="steelblue") +
        theme(axis.text.x=element_text(angle=90, vjust=0.5))
}

myplot <- plot_24h_load("uptime-YYYYMMDD.log")
myplot

ggsave("nebbiolo2_24h_load.png", plot=myplot, width=12, height=8, units="in", dpi=300)


###
### To put several 24-hour windows in the same plot (grouped bar plot)
###

compare_24h_loads <- function(uptime24_logs, colors)
{
    stopifnot(is.character(uptime24_logs), is.character(colors),
              length(uptime24_logs) == length(colors))
    dates <- names(uptime24_logs)
    if (is.null(dates))
        stop("'uptime24_logs' must be a named vector with the dates as names")
    dfs <- lapply(seq_along(uptime24_logs),
                  function(i) {
                      uptime24_log <- uptime24_logs[[i]]
                      df <- read_uptime24_log(uptime24_log)
                      df$date <- names(uptime24_logs)[[i]]
                      df
                  })
    df <- do.call(rbind, dfs)
    ggplot(df, aes(x=time, y=load, fill=date)) +
        geom_bar(position="dodge", stat="identity") +
        theme(axis.text.x=element_text(angle=90, vjust=0.5)) +
        scale_fill_manual(values=colors)
}

### Compare two tuesdays one week apart:
uptime24_logs <- c(`Oct 07`="uptime-251007.log", `Oct 14`="uptime-251014.log")
compare_24h_loads(uptime24_logs, c("steelblue", "salmon3"))

### More comparisons:
uptime24_logs <- c(`Oct 10`="uptime-251010.log",
                   `Oct 14`="uptime-251014.log",
                   `Oct 17`="uptime-251017.log")
colors <- c("steelblue", "salmon3", "seagreen4")
myplot <- compare_24h_loads(uptime24_logs, colors)

