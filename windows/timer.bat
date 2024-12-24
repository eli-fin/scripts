@python -c "exec('import time,sys \nstart = time.time() \nfor x in (range(int((sys.argv+[0])[1]))):\n time.sleep(1)\n print(int(time.time()-start))')" %1
