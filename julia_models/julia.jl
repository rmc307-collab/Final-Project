using Pkg 

Pkg.add("PyCall")

Pkg.build("PyCall")
Pkg.add(["CSV", "DataFrames", "Statistics", "MLJ", "BetaML", "StatisticalMeasures", "MLJModels", "MLJDecisionTreeInterface", "StatsBase", "JSON", "MLJLinearModels"])

function predict_peak_hours(file_path::String)
    df = CSV.read(file_path, DataFrame)
    model = LinearRegressor()
    X = select(df, Not(:Attendance))
    y = df.Attendance
    mach = machine(model, X, y)
    fit!(mach)
    preds = predict(mach, X)
    peak_time = X.Time[argmax(preds)]
    return "Predicted busiest hour: $(peak_time) with $(maximum(preds)) visitors"
end

