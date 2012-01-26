def AES(key):
    try:
        from crypto.cipher.cbc      import CBC
        from crypto.cipher.base     import noPadding
        from crypto.cipher.rijndael import Rijndael
        cipher = Rijndael(key, keySize=32, blockSize=16, padding=noPadding())
        return CBC(blockCipherInstance=cipher)
    except ImportError:
        print 'error'
        #from crypto.cipher.rijndael import Rijndael
        #from crypto.cipher.base     import noPadding
        #return Rijndael(key, keySize=32, blockSize=16, padding=noPadding())
