'''
自动白平衡，方法出自《A Fast Auto White Balance Scheme for Digital Pathology》
'''

import numpy as np
import skimage
from skimage import io

def EstimateIlluminantRGB(I, p):

    R = I[:,:,0]
    G = I[:,:,1]
    B = I[:,:,2]

    # Estimate Illuminant
    Rc = EstimateIlluminantGrey(R, p)
    Gc = EstimateIlluminantGrey(G, p)
    Bc = EstimateIlluminantGrey(B, p)
    
    return [Rc, Gc, Bc]


def EstimateIlluminantGrey(I, p):
    Ic = 0.0001 #改了
    
    L = 256
    sz = I.shape

    pxlTh = (p*sz[0]*sz[1])/100;
    histI = np.histogram(I, bins=256)

    Imin = np.min(I)
    Imax = np.max(I)

    # Run the loop from 0 to L-2 or Imin to Imax-1
    for k in range(Imin, Imax):    
        # Total number of pixels from k to L-1
        cnt1 = np.sum(histI[0][k:L])

        # Total number of pixels from k+1 to L-1
        k = k+1 # from the next grey value 
        cnt2 = np.sum(histI[0][k:L])

        if( (cnt1 > pxlTh) and (cnt2 < pxlTh) ):
            Ic = k
            break
    return Ic


def EstimateCCT(iEstm):
# Constant parameters from 

    A0 = -949.86315
    A1 = 6253.80338
    A2 = 28.70599
    A3 = 0.00004

    t1 = 0.92159
    t2 = 0.20039
    t3 = 0.07125

    xe = 0.3366
    ye = 0.1735

    # Calculate x and y from estimated illuminant values

    XYZ_Conv_matrix = np.asarray([ [0.4124, 0.3576, 0.1805],
                        [0.2126, 0.7152, 0.0722],
                        [0.0193, 0.152, 0.9505]])
    
    XYZ = XYZ_Conv_matrix @ np.asarray(iEstm).T
    
        
    x = XYZ[0] / (np.sum(XYZ))
    y = XYZ[1] / (np.sum(XYZ))

    H = -((x-xe)/(y-ye))

    CCT = A0 + (A1*np.exp(H/t1)) + (A2*np.exp(H/t2)) + (A3*np.exp(H/t3))
    return CCT

def ComputeGainFactorMatrix(iEstm):

    # k(r,g,b) = ig / i(r,g,b)

    iEstm_R = iEstm[0]
    iEstm_G = iEstm[1]
    iEstm_B = iEstm[2]

    iRef_R = iEstm_G
    iRef_G = iEstm_G 
    iRef_B = iEstm_G

    
    Kr = iRef_R / iEstm_R 
    Kg = iRef_G / iEstm_G
    Kb = iRef_B / iEstm_B

    K = np.asarray([
        [Kr, 0, 0],
        [0, Kg, 0],
        [0, 0, Kb]
    ])
                   
    return K


def ComputeOffsetMatrix(K, CCT_Estm, CCT_Ref):

    A = 100
        
    Kr = K[0,0]
    Kb = K[2,2]

    
    Tr = max(1, (CCT_Estm - CCT_Ref)/A)  * (Kr-1)
    Tg = 0
    Tb = max(1, (CCT_Ref - CCT_Estm)/A)  * (Kb-1)


    T = np.asarray((Tr, Tg, Tb))
    
    return T


def PerformWhiteBalanceCorrection(I, K, T):

    sz = I.shape
    O = (np.zeros(sz)).astype(np.uint8)

    O = np.einsum('...ij,...j->...i', K, I)+T
    O = np.clip(O, 0, 255)
                    
    return O


if __name__ == '__main__':

    I = skimage.io.imread('test_img/wb.jpg') #0~255

    # 默认参数

    p = 96
    p = 100-p; # always the top % is considered


    ##  Illumination Estimation

    # Step 1 : White Patch Retinex Mathod (WPR)
    [iR, iG, iB] = EstimateIlluminantRGB(I, p) 

    # Corelated Color Temperature (CCT) Estimation

    # Compte for estimated Illuminant
    iEstm = [iR, iG, iB]
    CCT_Estm = EstimateCCT(iEstm)

    # Compute for reference / canonical illuminant
    iRef = [iG, iG, iG]
    CCT_Ref = EstimateCCT(iRef)

    ## Parameter Estimation

    # Computing Gain Factor and offset parameters    
    K = ComputeGainFactorMatrix(iEstm)
    T = ComputeOffsetMatrix(K, CCT_Estm, CCT_Ref)

    ## White Balance Correction 

    O = PerformWhiteBalanceCorrection(I, K, T)


    io.imsave('test_img/wb_out.jpg', O)

