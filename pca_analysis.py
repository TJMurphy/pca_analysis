#!/usr/bin/env python

#
# Thomas Coudrat <thomas.coudrat@gmail.com>
# Janurary 2015
#

from __future__ import unicode_literals, print_function
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import argparse
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from sklearn.preprocessing import StandardScaler


def main():
    """
    Runs the pca_analysis script
    """

    # Collect arguments
    csvPath, rounded, proj3D, fl_save, fl_std, fl_log = parsing()

    # Prepare the data table
    df = pd.read_csv(filepath_or_buffer=csvPath, index_col=0, sep=",")
    colors = df.color.values
    dfData = df.drop("color", axis=1)
    samples = dfData.index.values
    features = dfData.columns.values

    # Apply data transformation if requested
    if fl_std:
        csvPath = csvPath.replace(".csv", "-std.csv")
        dfData = StandardScaler().fit_transform(dfData)
        dfData = pd.DataFrame(dfData)
    elif fl_log:
        csvPath = csvPath.replace(".csv", "-log.csv")
        dfData = dfData.apply(np.log)

    # Get the PCA for all dimensions (pc values)
    X_r, PCs, loadings = getPCA(dfData)

    # Displaying information to the terminal
    displaySaveLog(csvPath, df, dfData, PCs, loadings, features, fl_save,
                   fl_std, fl_log)

    # Round PC values for plotting
    PCs_round = [round(100 * pc, rounded) for pc in PCs]

    # Run the plotting function
    plotPCA(proj3D, X_r, PCs_round, samples, colors, csvPath, fl_save)


def parsing():
    """
    Parsing the parameters for script execution
    """

    descr = "Calculate PCA from data stored in a .csv file," \
        " and display it in a 2D plot (optional 3D)"
    descr_csvPath = "Path of the .csv file, each line is a" \
        " instance and the first value is its name followed" \
        " by its variables"
    descr_rounded = "Decimal at which principal components are rounded" \
        " (default=2)"
    descr_proj3D = "Use this flag for a 3D projection of the data"
    descr_save = "Use this flag if you want to save the figures upon execution"
    descr_std = "Use this flag to standardise the data to have 0 mean and" \
        " unit variance"
    descr_log = "Use this flag to apply a log to the data"

    parser = argparse.ArgumentParser(description=descr)

    parser.add_argument("csvPath", help=descr_csvPath)
    parser.add_argument("--rounded", type=int, help=descr_rounded)
    parser.add_argument("-proj3D", action="store_true", help=descr_proj3D)
    parser.add_argument("-save", action="store_true", help=descr_save)
    parser.add_argument("-std", action="store_true", help=descr_std)
    parser.add_argument("-log", action="store_true", help=descr_log)

    args = parser.parse_args()

    csvPath = args.csvPath
    # Default to rounded at second decimal if nothing else is provided
    if args.rounded:
        rounded = args.rounded
    else:
        rounded = 0
    proj3D = args.proj3D
    flag_save = args.save
    flag_std = args.std
    flag_log = args.log

    return csvPath, rounded, proj3D, flag_save, flag_std, flag_log


def getPCA(dfData):
    """
    Return the PCA data and principal component values given a dataset and a
    number of dimensions to be returned
    """

    # Get the PCA of that data
    pca = PCA()
    X_r = pca.fit_transform(dfData)

    # Check that the principal components have variance 1.0 which is equivalent
    # to each coefficient vector having norm 1.0
    coeffVectorNorms = np.linalg.norm(pca.components_.T, axis=0)
    print("Variance of PCs, check if equal to 1")
    print(coeffVectorNorms)

    # Check that the principal components can be calculated as the dot product
    # of the above coefficients and the original variables
    dotProduct = np.allclose(dfData.values.dot(pca.components_.T),
                             pca.fit_transform(dfData.values))
    print("PCs can be calculated as dot product of loadings and"
          " original values: " + str(dotProduct))

    return X_r, pca.explained_variance_ratio_, pca.components_


def displaySaveLog(csvPath, df, dfData, PCs, loadings, features, fl_save,
                   fl_std, fl_log):
    """
    Print out the information to the terminal
    """

    # Data table
    dataTitle = "\n## Data table ##\n"
    print(dataTitle)
    print(df)

    # Transformation
    print("\n## Transformed data ##\n")
    if fl_std:
        print("Standardised")
    elif fl_log:
        print("Logarithmic")
    print(dfData)

    # Principal components
    pcTitle = "\n## Principal Components ##\n"
    print(pcTitle)
    PC_names = []
    pcLines = []
    for i, pc in enumerate(PCs):
        currentPCname = "PC" + str(i+1)
        PC_names.append(currentPCname)
        pcLine = currentPCname + " = " + str(round(100*pc, 6)) + " %"
        print(pcLine)
        pcLines.append(pcLine + "\n")

    # Loadings
    loadTitle = "\n## Loadings ##\n"
    loadingsDf = pd.DataFrame(loadings, index=PC_names, columns=features)
    print(loadTitle)
    print(loadingsDf)

    # If the save flag was used
    if fl_save:

        # Saving loadings
        loadingsDf.to_csv(csvPath.replace(".csv", "_loadings.csv"))

        # Open file
        fileLog = open(csvPath.replace(".csv", "_info.txt"), "w")

        # Data table
        fileLog.write(dataTitle)
        df.to_csv(fileLog)

        # Principal components
        fileLog.write(pcTitle)
        for l in pcLines:
            fileLog.write(l)

        # Loadings
        fileLog.write(loadTitle)
        loadingsDf.to_csv(fileLog)

        # Close file!
        fileLog.close()


def plotPCA(proj3D, X_r, PCs, ligs, colors, csvPath, fl_save):
    """
    Plot the PCA data on 2D plot
    """

    # Main figure
    fig = plt.figure(figsize=(13, 12), dpi=100)

    if proj3D:
        ax = fig.add_subplot(111, projection="3d")
        for label, col, x, y, z in zip(ligs, colors,
                                       X_r[:, 0], X_r[:, 1], X_r[:, 2]):
            newCol = makeColor(col)
            Axes3D.scatter(ax, x, y, z, label=label, color=newCol,
                           marker="o", lw=1, s=800)
        ax.set_xlabel("PC1 (" + '{0:g}'.format(PCs[0]) + " %)", fontsize=30)
        ax.set_ylabel("PC2 (" + '{0:g}'.format(PCs[1]) + " %)", fontsize=30)
        ax.set_zlabel("PC3 (" + '{0:g}'.format(PCs[2]) + " %)", fontsize=30)
        ax.tick_params(axis="both", which="major", labelsize=20)
        pngPath = csvPath.replace(".csv", "_3D.png")
    else:
        ax = fig.add_subplot(111)
        for label, col, x, y in zip(ligs, colors, X_r[:, 0], X_r[:, 1]):
            newCol = makeColor(col)
            ax.scatter(x, y, label=label, color=newCol,
                       marker="o", lw=1, s=800)
            # ax.annotate(label, xy=(x, y - 0.05), fontsize=10,
            #             ha='center', va='top')
        ax.set_xlabel("PC1 (" + '{0:g}'.format(PCs[0]) + " %)", fontsize=30)
        ax.set_ylabel("PC2 (" + '{0:g}'.format(PCs[1]) + " %)", fontsize=30)
        ax.tick_params(axis="both", which="major", labelsize=30)
        pngPath = csvPath.replace(".csv", "_2D.png")

    # figTitle = "PCA on " + csvPath + " (PC1=" + pcVals[0] + ", PC2=" +
    # pcVals[1] + ")"
    # ax.text(0.5, 1.04, figTitle, horizontalalignment="center", fontsize=30,
    #         transform=ax.transAxes)

    # Legend figure
    fig_legend = plt.figure(figsize=(13, 12), dpi=100)
    plt.figlegend(*ax.get_legend_handles_labels(), scatterpoints=1,
                  loc="center", fancybox=True,
                  shadow=True, prop={"size": 30})

    # Save figures if save flag was used
    if fl_save:
        print("\nSAVING figures\n")
        fig.savefig(pngPath, bbox_inches="tight")
        fig_legend.savefig(pngPath.replace(".png", "_legend.png"))
    # Otherwise show the plots
    else:
        print("\nSHOWING figures\n")
        plt.show()


def makeColor(colorRGB):
    """
    Get a RGB color (1-255) as input, in string format R:G:B
    And return a RGB color (0-1)
    """
    return [float(col)/255. for col in colorRGB.split(":")]


if __name__ == "__main__":
    main()
