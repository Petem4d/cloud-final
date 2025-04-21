
firebase.initializeApp(config);

function initApp() {
    firebase.auth().onAuthStateChanged(user => {
      const signInButton = document.getElementById('signInButton');
      if (user) {
        // User is signed in.
        signInButton.innerText = 'Sign Out';
        document.getElementById('form').style.display = '';
      } else {
        // No user is signed in.
        signInButton.innerText = 'Sign In with Google';
        document.getElementById('form').style.display = 'none';
      }
    });
  }
  
  window.onload = function () {
      console.log('Running with auth enabled.');
      initApp();
  };
  
  function signIn() {
    const provider = new firebase.auth.GoogleAuthProvider();
    provider.addScope('https://www.googleapis.com/auth/userinfo.email');
    firebase
      .auth()
      .signInWithPopup(provider)
      .then(result => {
        // Returns the signed in user along with the provider's credential
        console.log(`${result.user.displayName} logged in.`);
        window.alert(`Welcome ${result.user.displayName}!`);
      })
      .catch(err => {
        console.log(`Error during sign in: ${err.message}`);
        window.alert(`Sign in failed. Retry or check your browser logs.`);
      });
  }
  
  function signOut() {
    firebase
      .auth()
      .signOut()
      .then(result => {})
      .catch(err => {
        console.log(`Error during sign out: ${err.message}`);
        window.alert(`Sign out failed. Retry or check your browser logs.`);
      });
  }
  
  // Toggle Sign in/out button
  function toggle() {
    if (!firebase.auth().currentUser) {
      signIn();
    } else {
      signOut();
    }
  }