# coding:utf-8

###############################################################
# CSVファイルを読込み、フィーチャ クラスを作成するスクリプト  #
###############################################################

"""
data フォルダをCドライブ直下に配置すればそのまま動作します。
任意の場所に配置する場合はデータの配置場所に合わせて変数の値を変更してください。
"""

import arcpy
import os
import datetime

######################################
# ワークスペースの設定
######################################
workPath = r"C:\data"
arcpy.env.workspace = workPath + r"\ArcMap\arcpy.gdb"

######################################
# PDF 出力先フォルダの作成
######################################
date = datetime.datetime.now()
dateStr = '{0:%Y%m%d}'.format(date)
# 現在の日時でフォルダを作成
os.makedirs(workPath + r"\output\{0}".format(dateStr))

######################################
# CSV ファイルを読込む
# ポイント フィーチャ クラスを作る
######################################
# ジオプロセシングツールに必要なパラメータの作成
csv_table = workPath + r"\current.csv"
out_csv_feature_class = "csv{0}".format(dateStr)
x_field = "X"
y_field = "Y"
event_layer = "csv_layer"
current_csv_feature_class = "current"

# ジオプロセシングツールの実行
arcpy.MakeXYEventLayer_management(csv_table, x_field, y_field, event_layer)
arcpy.FeatureClassToFeatureClass_conversion(event_layer, arcpy.env.workspace, out_csv_feature_class)
arcpy.DeleteFeatures_management(current_csv_feature_class)
arcpy.Append_management(out_csv_feature_class, current_csv_feature_class, "NO_TEST")

######################################
# 各駅ごとの放置車両数を集計する
######################################
# フィーチャクラス (curent) に対してカーソルを定義
cursor = arcpy.UpdateCursor("current")
# 23 区ごとに放置車両の合計値を算出
for row in cursor:
    row.setValue("放置車両_合計",row.getValue("放置台数_自転車") + row.getValue("放置台数_原付") + row.getValue("放置台数_自二"))
    cursor.updateRow(row)
del cursor, row

######################################
# 23 区ごとに地図を PDF 出力する
######################################
mxd = arcpy.mapping.MapDocument(workPath + r"\ArcMap\arcpy.mxd")
# データドリブンページで指定した図郭ごとに出力
for pageNum in range(1, mxd.dataDrivenPages.pageCount + 1):
    mxd.dataDrivenPages.currentPageID = pageNum
    print("{0}/{1}ページを出力中".format(str(pageNum), str(mxd.dataDrivenPages.pageCount)))
    arcpy.mapping.ExportToPDF(mxd, workPath + r"\output\{0}\report_{1}".format(dateStr, str(pageNum)) + ".pdf")