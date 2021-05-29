'''
自动白平衡，方法出自《A Fast Auto White Balance Scheme for Digital Pathology》
'''

import numpy as np
import numpy.matlib
from PIL import Image
import face_recognition




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


