if(is.na(Sys.getenv("RSTUDIO", unset = NA))){
  setwd(system2("pwd", stdout = TRUE)) # if not in RStudio, assume R runs in
} else {                               # a shell. otherwise assume RStudio
  path <- rstudioapi::getActiveDocumentContext()$path
  Encoding(path) <- "UTF-8"
  setwd(dirname(path))
}

library(dplyr)

getwd() # are we where we should be?

res <- read.csv2("res_temp1.csv")
res$A <- gsub("^ ", "", res$A) # remove eventual white space from 
                               # the beginning of the answers


# code the answers as numbers (as indicated by the leading number starting)
# the answer
res$A_num <- as.integer(sapply(strsplit(res$A, ""), `[`, 1))

## TO DO:
# sometimes (but rarely) there would be a mismatch between the
# answer option as indicated by the option number, and the verbal
# description, e.g. "1. I lean towards...", 
# need a check for this, and decide what to do with such answers.

res2 <- res |> group_by(model, Q) # group by model and question 
summarise(res2, var(A_num)) # do the models give varying answers
                            # to the same question?




