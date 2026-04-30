from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)

data = []

# ================== ROUTES ==================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        entry = {
            "nom": request.form.get("nom"),
            "age": int(request.form.get("age")),
            "sexe": request.form.get("sexe"),
            "classe": request.form.get("classe"),
            "niveau": request.form.get("niveau"),
            "internet": int(request.form.get("internet")),
            "environnement": int(request.form.get("environnement")),
            "note": float(request.form.get("note"))
        }

        data.append(entry)
        return redirect(url_for("dashboard"))

    return render_template("form.html")


@app.route("/dashboard")
def dashboard():
    if len(data) == 0:
        return render_template("dashboard.html", stats=None)

    df = pd.DataFrame(data)

    stats = {
        "moyenne": round(df["note"].mean(), 2),
        "max": df["note"].max(),
        "min": df["note"].min(),
        "total": len(df)
    }

    return render_template("dashboard.html", stats=stats)


@app.route("/analyse")
def analyse():
    if len(data) == 0:
        return "Aucune donnée"

    df = pd.DataFrame(data)

    # ================= STATISTIQUES =================
    moyenne = df["note"].mean()
    ecart_type = df["note"].std()
    Q1 = df["note"].quantile(0.25)
    Q2 = df["note"].median()
    Q3 = df["note"].quantile(0.75)
    IQR = Q3 - Q1

    # Z-score
    df["z_score"] = (df["note"] - moyenne) / ecart_type

    # ================= REGRESSION =================
    x = df["internet"]
    y = df["note"]
    coeffs = np.polyfit(x, y, 1)  # y = ax + b
    regression = np.poly1d(coeffs)

    # ================= GRAPHIQUES =================

    # Histogramme
    plt.figure()
    df["note"].hist()
    plt.title("Histogramme des notes")
    plt.savefig("static/hist.png")
    plt.close()

    # Diagramme en bâtons
    plt.figure()
    df.groupby("nom")["note"].mean().plot(kind="bar")
    plt.title("Notes par étudiant")
    plt.savefig("static/bar.png")
    plt.close()

    # Scatter + régression
    plt.figure()
    plt.scatter(x, y)
    plt.plot(x, regression(x))
    plt.title("Régression (Internet vs Note)")
    plt.savefig("static/regression.png")
    plt.close()

    stats = {
        "moyenne": round(moyenne, 2),
        "ecart_type": round(ecart_type, 2),
        "Q1": round(Q1, 2),
        "Q2": round(Q2, 2),
        "Q3": round(Q3, 2),
        "IQR": round(IQR, 2)
    }

    return render_template(
        "analyse.html",
        stats=stats,
        hist="static/hist.png",
        bar="static/bar.png",
        regression="static/regression.png"
    )


# ================= MAIN =================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        debug=False
    )
