# Setting Up Firestore for TikTok Content Performance Analyst

This guide will walk you through setting up Firestore for the TikTok Content Performance Analyst app.

## Step 1: Create a Firebase Project

1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" to create a new project
3. Enter a project name, e.g., "TikTok Content Analyst"
4. Enable Google Analytics if you want to (optional)
5. Click "Create project"

## Step 2: Set Up Firestore Database

1. In your Firebase project, click on "Firestore Database" in the left sidebar
2. Click "Create database"
3. Choose "Start in test mode" (for development)
4. Select a database location closest to your users
5. Click "Enable"

## Step 3: Set Up Security Rules

1. In the Firestore Database section, click on the "Rules" tab
2. Replace the existing rules with the following:

```
rules_version = '2';

service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```

3. Click "Publish"

> Note: These rules allow anyone to read and write to your database. For production, you should set up proper authentication rules.

## Step 4: Generate a Service Account Key

1. Click on the gear icon next to "Project Overview" and select "Project settings"
2. Go to the "Service accounts" tab
3. Under "Firebase Admin SDK", click "Generate new private key"
4. Click "Generate key" to download the JSON key file
5. Rename the downloaded file to `firebase_credentials.json`
6. Move the file to the root directory of your TikTok Content Performance Analyst project

## Step 5: Install Required Python Packages

Make sure you have the required packages installed:

```bash
pip install firebase-admin
```

## Step 6: Test the Connection

1. Run the test script to verify that your Firestore connection is working:

```bash
python test_firestore.py
```

If everything is set up correctly, you should see:
- "Firestore connected successfully"
- "Firestore connection test successful"
- Test report operations working properly

## Troubleshooting

### Connection Issues

- Ensure your `firebase_credentials.json` file is in the project root directory
- Verify that the credentials in the file are correct
- Check your internet connection
- Make sure you've enabled Firestore in your Firebase project

### Permission Issues

- Verify that your Firestore security rules are set correctly
- Ensure your service account has proper permissions in Firebase

## Additional Information

- For production use, you should restrict access using proper authentication rules
- Consider setting up backup solutions for your Firestore data 