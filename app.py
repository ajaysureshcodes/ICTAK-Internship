from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import pickle

app = Flask(__name__)
app.secret_key = 'your_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

knn1 = pickle.load(open('knn1.pkl', 'rb'))
knn2 = pickle.load(open('knn2.pkl', 'rb'))
knn3 = pickle.load(open('knn3.pkl', 'rb'))

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':  # Simple check
            user = User(1)
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        # Collect numerical features
        features = [float(request.form[feature]) for feature in [
            'Num_of_Delayed_Payment', 'Num_Bank_Accounts',
            'Interest_Rate', 'Changed_Credit_Limit', 'Num_Credit_Card',
            'Credit_History_Age', 'Delay_from_due_date'
        ]]

        # Handle the categorical 'Payment_of_Min_Amount'
        payment_of_min_amount = request.form['Payment_of_Min_Amount']
        if payment_of_min_amount == 'Yes':
            payment_of_min_amount_value = 1
        else:
            payment_of_min_amount_value = 0
        
        # Include payment_of_min_amount_value in features
        features.insert(0, payment_of_min_amount_value)

        apredict = [features]
        
        # Get predictions from the models
        results1 = knn1.predict(apredict)
        results2 = knn2.predict(apredict)
        results3 = knn3.predict(apredict)
        
        # Combine predictions
        prediction = []
        for r1, r2, r3 in zip(results1, results2, results3):
            if r1 == 1 and r2 == 1:
                prediction.append(r1)
            elif r1 == 0 or r2 == 0:
                prediction.append(r3)
            else:
                prediction.append(r1)
        
        final_prediction = prediction[0]
        
        # Map final prediction to credit score
        if final_prediction == 1:
            credit_score = 'Poor'
        elif final_prediction == 2:
            credit_score = 'Standard'
        else:
            credit_score = 'Good'
        
        return render_template('result.html', prediction=credit_score)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)