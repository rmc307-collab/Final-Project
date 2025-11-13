
using CSV, DataFrames, Statistics, MLJ, MLJLinearModels

# Convert 24-hour integer (e.g. 20) to 12-hour AM/PM format
function format_hour(hour::Int)
    if hour == 0
        return "12 AM"
    elseif hour < 12
        return string(hour, " AM")
    elseif hour == 12
        return "12 PM"
    else
        return string(hour - 12, " PM")
    end
end

"""
    predict_peak_hours(file_path::String)

Reads attendance data (with Location, Time, Attendance, Cleanliness, Date),
fits linear regression per gym location, predicts busiest hour,
and also computes correlation between attendance and cleanliness.

Returns a detailed text summary for each gym.
"""
function predict_peak_hours(file_path::String)
    # Load attendance data
    df = CSV.read(file_path, DataFrame)
    rename!(df, Symbol.(["Location", "Time", "Attendance", "Cleanliness", "Date"]))

    # Convert columns only if they are strings
if eltype(df.Time) <: AbstractString
    df.Time = parse.(Int, df.Time)
end

if eltype(df.Attendance) <: AbstractString
    df.Attendance = parse.(Float64, df.Attendance)
end

if eltype(df.Cleanliness) <: AbstractString
    df.Cleanliness = parse.(Float64, df.Cleanliness)
end

    # Initialize model
    model = LinearRegressor()
    results = String[]

    for loc in unique(df.Location)
        subdf = filter(row -> row.Location == loc, df)
        X = select(subdf, :Time)
        y = subdf.Attendance

        # Train regression model for attendance vs time
        mach = machine(model, X, y)
        fit!(mach)

        # Predict attendance for all hours (0–23)
        # Limit predictions to realistic gym hours (based on your data)
        min_hour = minimum(subdf.Time)
        max_hour = maximum(subdf.Time)
        newdata = DataFrame(Time = min_hour:max_hour)
        preds = predict(mach, newdata)

        # Find peak and ideal hour
        max_idx = argmax(preds)
        peak_hour = newdata.Time[max_idx]
        max_att = round(preds[max_idx], digits=1)

        # 🧼 Find cleanest hour (highest cleanliness score)
        clean_idx = argmax(subdf.Cleanliness)
        clean_hour = subdf.Time[clean_idx]
        clean_score = subdf.Cleanliness[clean_idx]

        # Compute correlation (cleanliness vs attendance)
        corr_val = cor(subdf.Attendance, subdf.Cleanliness)

        # Determine the best hour for "balance" — moderate attendance & high cleanliness
        # Weighted score: (10 - normalized attendance) + cleanliness
        att_norm = (subdf.Attendance .- minimum(subdf.Attendance)) ./ 
                   (maximum(subdf.Attendance) - minimum(subdf.Attendance) + 1e-6)
        score = (10 .- (att_norm .* 10)) .+ subdf.Cleanliness
        best_idx = argmax(score)
        best_hour = subdf.Time[best_idx]
        best_clean = subdf.Cleanliness[best_idx]

        # 🕒 Round hours to nearest of [8, 12, 20]
        possible_hours = [8, 12, 20]
        nearest_hour(h) = possible_hours[argmin(abs.(possible_hours .- h))]
        peak_hour = nearest_hour(peak_hour)
        clean_hour = nearest_hour(clean_hour)
        best_hour = nearest_hour(best_hour)

        # Add readable summary
        summary = """
        🏋️ Gym: $(loc)
        • Predicted busiest hour: $(format_hour(peak_hour))  (~$(max_att) people)
        • Cleanest hour: $(format_hour(clean_hour))  (Cleanliness = $(clean_score))
        • Cleanliness correlation with attendance: $(round(corr_val, digits=2))
        • Ideal visiting time (balance crowd + cleanliness): $(format_hour(best_hour))
        (Cleanliness = $(best_clean))
        """
        
        push!(results, summary)
    end

    return join(results, "\n" * repeat("-", 50) * "\n")
end

