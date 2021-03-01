'''
自动白平衡，方法出自《A Fast Auto White Balance Scheme for Digital Pathology》
'''

import numpy as np
import numpy.matlib
from PIL import Image
import face_recognition

from sympy.solvers import solve
from sympy import Symbol  


class WBsRGB:
  def __init__(self, gamut_mapping=2, upgraded=0):
    if upgraded == 1:
      self.features = np.load('models/features+.npy')  # encoded features
      self.mappingFuncs = np.load('models/mappingFuncs+.npy')  # correct funcs
      self.encoderWeights = np.load('models/encoderWeights+.npy')  # PCA matrix
      self.encoderBias = np.load('models/encoderBias+.npy')  # PCA bias
      self.K = 75  # K value for NN searching
    else:
      self.features = np.load('models/features.npy')  # encoded features
      self.mappingFuncs = np.load('models/mappingFuncs.npy')  # correction funcs
      self.encoderWeights = np.load('models/encoderWeights.npy')  # PCA matrix
      self.encoderBias = np.load('models/encoderBias.npy')  # PCA bias
      self.K = 25  # K value for nearest neighbor searching

    self.sigma = 0.25  # fall-off factor for KNN blending
    self.h = 60  # histogram bin width
    # our results reported with gamut_mapping=2, however gamut_mapping=1
    # gives more compelling results with over-saturated examples.
    self.gamut_mapping = gamut_mapping  # options: 1 scaling, 2 clipping

  def encode(self, hist):
    """ Generates a compacted feature of a given RGB-uv histogram tensor."""
    histR_reshaped = np.reshape(np.transpose(hist[:, :, 0]),
                                (1, int(hist.size / 3)), order="F")
    histG_reshaped = np.reshape(np.transpose(hist[:, :, 1]),
                                (1, int(hist.size / 3)), order="F")
    histB_reshaped = np.reshape(np.transpose(hist[:, :, 2]),
                                (1, int(hist.size / 3)), order="F")
    hist_reshaped = np.append(histR_reshaped,
                              [histG_reshaped, histB_reshaped])
    feature = np.dot(hist_reshaped - self.encoderBias.transpose(),
                     self.encoderWeights)
    return feature

  def rgb_uv_hist(self, I):
    """ Computes an RGB-uv histogram tensor. """
    sz = np.shape(I)  # get size of current image
    if sz[0] * sz[1] > 202500:  # resize if it is larger than 450*450
      factor = np.sqrt(202500 / (sz[0] * sz[1]))  # rescale factor
      newH = int(np.floor(sz[0] * factor))
      newW = int(np.floor(sz[1] * factor))
      # I = cv2.resize(I, (newW, newH), interpolation=cv2.INTER_NEAREST) #再加个cv2太臃肿了，用PIL替代
      I_switch = Image.fromarray(np.uint8(I*255))
      I_switch = I_switch.resize((newW, newH))
      I = np.float32(np.asarray(I_switch)/255)

    I_reshaped = I[(I > 0).all(axis=2)]
    eps = 6.4 / self.h
    hist = np.zeros((self.h, self.h, 3))  # histogram will be stored here
    Iy = np.linalg.norm(I_reshaped, axis=1)  # intensity vector
    for i in range(3):  # for each histogram layer, do
      r = []  # excluded channels will be stored here
      for j in range(3):  # for each color channel do
        if j != i:
          r.append(j)
      Iu = np.log(I_reshaped[:, i] / I_reshaped[:, r[1]])
      Iv = np.log(I_reshaped[:, i] / I_reshaped[:, r[0]])
      hist[:, :, i], _, _ = np.histogram2d(
        Iu, Iv, bins=self.h, range=((-3.2 - eps / 2, 3.2 - eps / 2),) * 2, weights=Iy)
      norm_ = hist[:, :, i].sum()
      hist[:, :, i] = np.sqrt(hist[:, :, i] / norm_)  # (hist/norm)^(1/2)
    return hist

  def correctImage(self, I, hald):
    """ White balance a given image I. """
    feature = self.encode(self.rgb_uv_hist(I))
    # Do
    # ```python
    # feature_diff = self.features - feature
    # D_sq = np.einsum('ij,ij->i', feature_diff, feature_diff)[:, None]
    # ```
    D_sq = np.einsum(
      'ij, ij ->i', self.features, self.features)[:, None] + np.einsum(
      'ij, ij ->i', feature, feature) - 2 * self.features.dot(feature.T)

    # get smallest K distances
    idH = D_sq.argpartition(self.K, axis=0)[:self.K]
    mappingFuncs = np.squeeze(self.mappingFuncs[idH, :])
    dH = np.sqrt(
      np.take_along_axis(D_sq, idH, axis=0))
    sorted_idx = dH.argsort(axis=0)  # get sorting indices
    dH = np.take_along_axis(dH, sorted_idx, axis=0)  # sort distances
    weightsH = np.exp(-(np.power(dH, 2)) /
                      (2 * np.power(self.sigma, 2)))  # compute weights
    weightsH = weightsH / sum(weightsH)  # normalize blending weights
    mf = sum(np.matlib.repmat(weightsH, 1, 33) *
             mappingFuncs, 0)  # compute the mapping function
    mf = mf.reshape(11, 3, order="F")  # reshape it to be 9 * 3
    I_corr = self.colorCorrection(hald, mf)  # apply it!
    return I_corr

  def colorCorrection(self, input, m):
    """ Applies a mapping function m to a given input image. """
    sz = np.shape(input)  # get size of input image
    I_reshaped = np.reshape(input, (int(input.size / 3), 3), order="F")
    kernel_out = kernelP(I_reshaped)
    out = np.dot(kernel_out, m)
    if self.gamut_mapping == 1:
      # scaling based on input image energy
      out = normScaling(I_reshaped, out)
    elif self.gamut_mapping == 2:
      # clip out-of-gamut pixels
      out = outOfGamutClipping(out)
    else:
      raise Exception('Wrong gamut_mapping value')
    # reshape output image back to the original image shape
    out = out.reshape(sz[0], sz[1], sz[2], order="F")
    return out


def normScaling(I, I_corr):
  """ Scales each pixel based on original image energy. """
  norm_I_corr = np.sqrt(np.sum(np.power(I_corr, 2), 1))
  inds = norm_I_corr != 0
  norm_I_corr = norm_I_corr[inds]
  norm_I = np.sqrt(np.sum(np.power(I[inds, :], 2), 1))
  I_corr[inds, :] = I_corr[inds, :] / np.tile(
    norm_I_corr[:, np.newaxis], 3) * np.tile(norm_I[:, np.newaxis], 3)
  return I_corr


def kernelP(rgb):
  """ Kernel function: kernel(r, g, b) -> (r,g,b,rg,rb,gb,r^2,g^2,b^2,rgb,1)
        Ref: Hong, et al., "A study of digital camera colorimetric
          characterization based on polynomial modeling." Color Research &
          Application, 2001. """
  r, g, b = np.split(rgb, 3, axis=1)
  return np.concatenate(
    [rgb, r * g, r * b, g * b, rgb ** 2, r * g * b, np.ones_like(r)], axis=1)


def outOfGamutClipping(I):
  """ Clips out-of-gamut pixels. """
  I[I > 1] = 1  # any pixel is higher than 1, clip it to 1
  I[I < 0] = 0  # any pixel is below 0, clip it to 0
  return I

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

def auto_wb_correct(img, hald_img, face=False):
    '''
    自动白平衡校正，根据原图去估计，变换矩阵应用到 hald 上
    '''
    img = np.uint8(img*255)
    hald_img = np.uint8(hald_img*255)

    if face:
        face_locations = face_recognition.face_locations(img) #默认用 hog 而不是 cnn
        if len(face_locations) != 0:
            top, right, bottom, left = face_locations[0] #用找到的第一个脸
            img = img[top:bottom, left:right]
        else:
            print("并没有找到人脸")


    # 默认参数
    p = 96
    p = 100-p; # always the top % is considered

    ##  Illumination Estimation

    # Step 1 : White Patch Retinex Mathod (WPR)
    [iR, iG, iB] = EstimateIlluminantRGB(img, p) 

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

    out_hald = PerformWhiteBalanceCorrection(hald_img, K, T)
    out_hald = np.float64(out_hald/255)

    return out_hald

def auto_wb_correct_qcgp(img, hald_img):
    '''
    使用 QCGP 方法的自动白平衡。速度很慢，但翻车率低一些。
    '''
    r_ave = np.mean(img[:,:,0])
    g_ave = np.mean(img[:,:,1])
    b_ave = np.mean(img[:,:,2])
    k_ave = (r_ave+g_ave+b_ave)/3

    r_max = np.max(img[:,:,0])
    g_max = np.max(img[:,:,1])
    b_max = np.max(img[:,:,2])
    k_max = (r_max+g_max+b_max)/3


    r_u = Symbol('u')
    r_v = Symbol('v')
    s = solve([r_u*r_ave**2+r_v*r_ave-k_ave, r_u*r_max**2+r_v*r_max-k_max], [r_u,r_v])
    r_u = s.get(r_u)
    r_v = s.get(r_v)

    g_u = Symbol('u')
    g_v = Symbol('v')
    s = solve([g_u*g_ave**2+g_v*g_ave-k_ave, g_u*g_max**2+g_v*g_max-k_max], [g_u,g_v])
    g_u = s.get(g_u)
    g_v = s.get(g_v)

    b_u = Symbol('u')
    b_v = Symbol('v')
    s = solve([b_u*b_ave**2+b_v*b_ave-k_ave, b_u*b_max**2+b_v*b_max-k_max], [b_u,b_v])
    b_u = s.get(b_u)
    b_v = s.get(b_v)

    qcgp = np.zeros((hald_img.shape))

    qcgp[:,:,0] = hald_img[:,:,0]**2*r_u + hald_img[:,:,0]*r_v
    qcgp[:,:,1] = hald_img[:,:,1]**2*g_u + hald_img[:,:,1]*g_v
    qcgp[:,:,2] = hald_img[:,:,2]**2*b_u + hald_img[:,:,2]*b_v
    return qcgp


def auto_wb_srgb(img, hald_img, face = False):
    '''
    "When color constancy goes wrong: Correcting improperly white-balanced images", CVPR 2019.
    https://github.com/mahmoudnafifi/WB_sRGB
    '''        
    # use upgraded_model= 1 to load our new model that is upgraded with new training examples.
    upgraded_model = 1
    # use gamut_mapping = 1 for scaling, 2 for clipping (our paper's results reported using clipping). If the image is over-saturated, scaling is recommended.
    gamut_mapping = 2

    if face:
        face_locations = face_recognition.face_locations(np.uint8(img*255)) #默认用 hog 而不是 cnn
        if len(face_locations) != 0:
            top, right, bottom, left = face_locations[0] #用找到的第一个脸
            img = img[top:bottom, left:right]
        else:
            print("并没有找到人脸")

    # processing
    # create an instance of the WB model
    wbModel = WBsRGB(gamut_mapping=gamut_mapping,
                            upgraded=upgraded_model)
    outImg = wbModel.correctImage(img, hald_img)  # white balance it
    return outImg


