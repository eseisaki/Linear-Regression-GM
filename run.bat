@ECHO OFF
SETLOCAL
SET CHOICE=2
SET NEW_DATASET=drift
SET K=10
SET POINTS=5000
SET EPOCH=4
SET VAR=10
SET FEATURES=10
SET VPER=0.25
SET ERROR=0.02
SET WIN_SIZE=3000
SET WIN_STEP=1
SET TEST=False
SET DEBUG=False
SET IN_FILE=io_files/drift
SET OUT_FILE=io_files/fgm_nodes_10_features_10_error_0.02_epoch_4

python main.py %CHOICE% %NEW_DATASET% %K% %POINTS% %EPOCH% %VAR% %FEATURES% %VPER% %ERROR% %WIN_SIZE% %WIN_STEP% %TEST% %DEBUG% %IN_FILE% %OUT_FILE%

PAUSE