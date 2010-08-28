def AES(key):
    try:
        from crypto.cipher.rijndael import Rijndael
        from crypto.cipher.base     import noPadding
        return Rijndael(key, keySize=32, blockSize=16, padding=noPadding())
    except ImportError:
        from crypto.cipher.rijndael import Rijndael
        from crypto.cipher.base     import noPadding
        return Rijndael(key, keySize=32, blockSize=16, padding=noPadding())
