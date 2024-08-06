if(is.na(Sys.getenv("RSTUDIO", unset = NA))){
  setwd(system2("pwd", stdout = TRUE)) # if not in RStudio, assume R runs in
} else {                               # a shell. otherwise assume RStudio
  path <- rstudioapi::getActiveDocumentContext()$path
  Encoding(path) <- "UTF-8"
  setwd(dirname(path))
}

library(data.table)
ll <- read.csv2("mem_afirst04082024-00h42m.csv")
ll <- as.data.table(ll)
alabel <- sapply(1:27, \(x) rep(x,2), simplify = FALSE) |> unlist()
rr <- nrow(ll) / length(alabel)
ll[,Question := rep(alabel, rr)]
ll[,Antinomy := rep(c("P","N"), nrow(ll)/2)]
ll[,Presentation_Order := rep(c(1,2), nrow(ll)/2)]
ll[,A := gsub("^ *", "", ll$A)]

legit_a <- "^It is correct|^It is partially correct|^It is partially incorrect|^It is incorrect|^Other"
legit_a_idx <- grep(legit_a, ll$A)
ll <- ll[legit_a_idx,]

ll[,A := regmatches(ll$A, regexpr(legit_a, ll$A))]

write.csv2(ll, "prompt3.1_Pfirst_cleaned.csv")
     