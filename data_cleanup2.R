if(is.na(Sys.getenv("RSTUDIO", unset = NA))){
  setwd(system2("pwd", stdout = TRUE)) # if not in RStudio, assume R runs in
} else {                               # a shell. otherwise assume RStudio
  path <- rstudioapi::getActiveDocumentContext()$path
  Encoding(path) <- "UTF-8"
  setwd(dirname(path))
}

getwd()

library(data.table)
lln <- read.csv2("FILENAME.csv")
lln <- as.data.table(lln)
# alabel <- sapply(1:27, \(x) rep(x,2), simplify = FALSE) |> unlist()
# rr <- nrow(ll) / length(alabel)
# ll[,Question := rep(alabel, rr)]
# ll[,Antinomy := rep(c("N","P"), nrow(ll)/2)]
# ll[,Presentation_Order := rep(c(1,2), nrow(ll)/2)]
lln[,A := gsub("^ *", "", lln$A)]
lln[,A := sapply(strsplit(ll$A, ""), `[[`, 1)]
#table(lln$model)
#lln <- ll[model != "llama2:7b-chat-q4_0",] 

lln[,A := as.integer(A)]
lln[,mean(A), by =c("model", "Question", "Antinomy", "temperature")]

lltmean <- dcast(lln, Question + model + temperature ~ Antinomy, 
             value.var = "A", fun.agg = \(x) mean(x))

lltvar <- dcast(lln, Question + model + temperature ~ Antinomy, 
             value.var = "A", fun.agg = \(x) var(x))
setnames(lltmean, c("N", "P"), c("Nmean", "Pmean"))
setnames(lltvar, c("N", "P"), c("Nvar", "Pvar"))

llcomb <- lltmean[lltvar]
#llcomb[A == 5]
# llcomb[(!(Nmean + Pmean > 6 | Nmean + Pmean < 3) | Nmean + Pmean == 10) & Nvar > 0.5 & Pvar > 0.5,
#        mean(as.numeric(temperature))]
# 
# llcomb[Nvar <= 0.001 | Pvar <= 0.001, table(Question)] 
# 
# llcomb[temperature == "2.0",] 
# 
# llcomb
write_csv2(llcomb, "0-2_temps_small_models.csv")

# lltmean[model == "gemma:2b-instruct-v1.1-q4_0", N-P, by = c("temperature", "Question")]
# lltvar[model == "gemma:2b-instruct-v1.1-q4_0", P, by = c("temperature", "Question")]
# 
# lln[,var(A), by =c("model", "Question", "Antinomy", "temperature")][temperature == "2.0"]
# 
# 
# lln[model == "gemma:7b-instruct-v1.1-q4_0" & 
#       temperature == "2.0" & Question == 1 & Antinomy == "N", table(A)]
# 
# legit_a <- "I agree|I lean towards agreeing|I lean towards disagreeing|I disagree|Other"
# legit_a_idx <- grep(legit_a, ll$A)
# ll <- ll[legit_a_idx,]
# 
# ll[,A := regmatches(ll$A, regexpr(legit_a, ll$A))]
# table(ll$A)
# 
# write.csv2(ll, "agree_ctrl_nfirst_htemp_anylegit.csv")
# 
# ### merge data sets to create "no conversational memory" data
# 
# pfirst <- as.data.table(read.csv2("agree_ctrl_pfirst_htemp_anylegit.csv"))
# pfirst <- pfirst[Antinomy == "P",]
# table(pfirst$Antinomy)
# 
# nfirst <- as.data.table(read.csv2("agree_ctrl_nfirst_htemp_anylegit.csv"))
# nfirst <- nfirst[Antinomy == "N",]
# sum(nfirst$Presentation_Order)
# 
# nomem <- rbind(pfirst, nfirst)
# write.csv2(nomem, "agree_ctrl_no_memory_htemp_anylegit.csv")
# 
# a <- as.data.table(read.csv2("prompt3.1_Nfirst_cleaned.csv"))
# 
# a <- as.data.table(read.csv2("prompt3.1_Nfirst_cleaned.csv"))
# a[,A := as.numeric(as.factor(A))]
# a[,var(A), by = list(model, Q, temperature)][V1>0,.N, by = temperature]
# a[,.N,by=list(temperature,Q)]
# 
# a[, var(A), by=list(model,Q)]
# 
# 
# 
# 
# a[temperature == 0.1][V1 > 0]
# a[, var(X)]
# 
