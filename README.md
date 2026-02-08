# Face Recognition and Verification using MTCNN, FaceNet, and KNN

This project implements a complete **face recognition and verification pipeline** using deep learning–based feature extraction and similarity matching. The system processes raw images, detects and crops faces using MTCNN, generates embeddings using FaceNet, and performs identity recognition using a K-Nearest Neighbors (KNN) classifier.

The framework is designed to organize large image datasets efficiently and perform reliable face identification and verification based on learned facial embeddings.

---

## Overview

The project builds an end-to-end face recognition system consisting of dataset organization, face detection, feature extraction, and identity prediction. Images are first structured using metadata generation, followed by face localization using MTCNN. Extracted faces are converted into numerical embeddings using FaceNet, which capture unique facial features.

Recognition is performed using a KNN classifier trained on embedding vectors, while cosine similarity is used as an additional verification step to confirm identity matches.

This modular pipeline allows easy extension for large-scale identity verification and biometric applications.

---

## Features

- Automated metadata generation with timestamps
- Structured dataset organization by constituency and voter ID
- Face detection and cropping using MTCNN
- Deep feature extraction using FaceNet embeddings
- Face recognition using KNN classifier
- Identity verification using cosine similarity
- Scalable and modular pipeline design

---

## Method Overview

The system operates in the following stages:

1. **Metadata Generation**
   - Scans dataset folders.
   - Creates a CSV file containing constituency, voter ID, image path, and timestamp.

2. **Face Detection (MTCNN)**
   - Detects faces in images.
   - Crops and stores detected faces in structured directories.

3. **Feature Extraction (FaceNet)**
   - Cropped faces are resized and normalized.
   - FaceNet generates 128-dimensional embedding vectors.

4. **Recognition (KNN)**
   - KNN classifier is trained on existing embeddings.
   - New face embeddings are compared against stored embeddings.

5. **Verification**
   - Cosine similarity is computed between embeddings.
   - Threshold-based verification confirms identity.

---

## Technologies Used

- Python
- OpenCV
- MTCNN (Face Detection)
- FaceNet (Deep Embeddings)
- NumPy
- Pandas
- scikit-learn (KNN Classifier)
- Cosine Similarity Metrics

---

## Project Workflow
Raw Images\
↓\
Metadata Generation (CSV)\
↓\
Face Detection (MTCNN)\
↓\
Cropped Faces\
↓\
FaceNet Embeddings\
↓\
KNN Classification\
↓\
Cosine Similarity Verification\


---

## Usage

### Step 1: Generate Metadata

Create metadata CSV from dataset folders:

```bash
python Fake vote detection.ipynb


