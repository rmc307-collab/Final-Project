using Pkg 

Pkg.add("PyCall")

Pkg.build("PyCall")
Pkg.add(["CSV", "DataFrames", "Statistics", "MLJ", "BetaML", "StatisticalMeasures", "MLJModels", "MLJDecisionTreeInterface", "StatsBase", "JSON"])

