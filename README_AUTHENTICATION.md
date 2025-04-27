# Firebase Authentication Setup

This application is configured to only allow a single admin user to access the TikTok Content Performance Analyst tool.

## Authentication Flow

The app uses Firebase Authentication to restrict access to only the admin user with the specific UID: `c88yBt47V0Taddds4nkmzL4Da1i1`.

## Setup Instructions

To set up your Firebase Authentication:

1. **Create a Firebase Project** (if you haven't already)

   - Go to the [Firebase Console](https://console.firebase.google.com/)
   - Create a new project or use your existing one

2. **Enable Email/Password Authentication**

   - In the Firebase Console, navigate to "Authentication"
   - Click on "Sign-in method" tab
   - Enable the "Email/Password" provider

3. **Create Your Admin User**

   - Go to the "Users" tab in Authentication
   - Click "Add User"
   - Enter your email and password
   - This will create a new user that you'll use to log in

4. **Verify User UID**

   - After creating the user, you'll see its UID in the users list
   - Verify that this UID matches `c88yBt47V0Taddds4nkmzL4Da1i1`
   - If it doesn't match, you'll need to update the UID in two places:
     - In `app.py`: Update the `ADMIN_UID` constant
     - In `firestore.rules`: Update the UID in the security rules

5. **Deploy Firestore Rules**
   - Make sure the `firestore.rules` file contains the correct UID
   - Deploy the rules to Firebase with:
     ```
     firebase deploy --only firestore:rules
     ```

## Login Process

When you start the application:

1. You'll be presented with a login screen
2. Enter the email and password for your admin account
3. The system will verify your UID against the allowed admin UID
4. If they match, you'll be granted access to the application

## Troubleshooting

If you can't access the app:

1. **Check Credentials**: Make sure you're using the correct email and password
2. **Verify UID**: Confirm that your user's UID matches the one in the code and Firestore rules
3. **Firebase Configuration**: Ensure the Firebase config in `.env` is correct
4. **Firebase Rules**: Make sure the Firestore rules are deployed correctly
