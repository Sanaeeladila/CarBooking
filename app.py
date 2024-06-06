from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from bson import ObjectId  # Importez ObjectId depuis bson
from datetime import datetime
from flask import jsonify
from werkzeug.utils import secure_filename
import os
from flask import session
import pdfkit
from flask import make_response, send_from_directory

UPLOAD_FOLDER = 'static/images'  # Dossier où les images seront enregistrées
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Extensions de fichiers autorisées


app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = "hfkslmz,rncyrb187649"  # Replace with a strong secret key
client = MongoClient('localhost', 27017)
db = client['location_voitures']  # Replace with your MongoDB database name
users_collection = db['users']
cars_collection = db['cars']
clients_collection = db['clients']
reservations_collection = db['reservations']

@app.route('/')
def index():
    # Récupérer toutes les voitures depuis la collection dans la base de données MongoDB
    cars_data = cars_collection.find({'state': 'active'})
    cars_list = list(cars_data)  # Convertir le curseur en une liste de dictionnaires
    return render_template('index.html', cars=cars_list)


@app.route('/manager')
def manager_dashboard():
    # Récupération des nombres de voitures, clients et réservations en attente
    car_count = cars_collection.count_documents({'state': 'active'})
    nbrclient = clients_collection.count_documents({'state': 'active'})
    nbrreservations = reservations_collection.count_documents({'status': 'en attente'})
    # Stockage des valeurs dans la session
    session['car_count'] = car_count
    session['client_count'] = nbrclient
    session['reservations_count'] = nbrreservations
    return render_template('managerDashbord.html', car_count=car_count, client_count=nbrclient, reservations_count=nbrreservations)


@app.route('/cars')  # Cette route correspond à la page pour les voitures
def cars():
    # Récupérer toutes les voitures depuis la collection dans la base de données MongoDB
    cars_data = cars_collection.find({'state': 'active'})
    cars_list = list(cars_data)  # Convertir le curseur en une liste de dictionnaires
    return render_template('cars.html', cars=cars_list)



@app.route('/add_car')  # Cette route correspond à la page pour les managers
def add_car():
    return render_template('add_car.html')


@app.route('/add_car', methods=['POST'])
def add_car_DB():
    brand = request.form.get('brand')
    model = request.form.get('model')
    year = request.form.get('year')
    color = request.form.get('color')
    mileage = request.form.get('mileage')
    price = request.form.get('price')
    #status = request.form.get('status')
    filename = None
    # Vérifier si le champ 'picture' est dans la requête et que le fichier est valide
    if 'picture' in request.files:
        file = request.files['picture']
        if file.filename != '' and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
            filename = secure_filename(file.filename)
            # Assurez-vous que le dossier d'upload existe
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            # Enregistrez le fichier dans le dossier d'upload
            file.save(os.path.join(UPLOAD_FOLDER, filename))
        else:
            return render_template('add_car.html', addcar_error="Invalid file format! Allowed formats are: png, jpg, jpeg, gif")
    # Insérer les données dans MongoDB avec le nom de fichier de l'image
    car_data = {
        'brand': brand,
        'model': model,
        'year': year,
        'color': color,
        'mileage': mileage,
        'price': price,
        'status': 'available',
        'image': filename,
        'state': 'active'
    }
    cars_collection.insert_one(car_data)
    return render_template('add_car.html', addcar_valid="Car added successfully!")

@app.route('/update_car', methods=['GET'])
def update_car():
    car_id = request.args.get('car_id')  # Récupérez l'identifiant de la voiture à partir de la requête GET
    car = cars_collection.find_one({'_id': ObjectId(car_id)})  # Récupérez les informations de la voiture à partir de la base de données
    return render_template('update_car.html', car=car)


@app.route('/update_car', methods=['POST'])
def update_car_BD():
    # Récupérez les données du formulaire
    car_id = request.form.get('id')
    brand = request.form.get('brand')
    model = request.form.get('model')
    year = request.form.get('year')
    color = request.form.get('color')
    mileage = request.form.get('mileage')
    price = request.form.get('price')
    status = request.form.get('status')
    filename = None
    car = cars_collection.find_one({'_id': ObjectId(car_id)})
    # Mettez à jour les informations de la voiture dans la base de données
    update_query = {
        'brand': brand,
        'model': model,
        'year': year,
        'color': color,
        'mileage': mileage,
        'price': price,
        'status': status
    }
    # Vérifier si le champ 'picture' est dans la requête et que le fichier est valide
    #print("Request files:", request.files)
    if 'picture' in request.files:
        file = request.files['picture']
        #print("Filename:", file.filename)
        if file.filename != '':
            if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                filename = secure_filename(file.filename)
                # Assurez-vous que le dossier d'upload existe
                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)
                # Enregistrez le fichier dans le dossier d'upload
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                update_query['image'] = filename
            else:
                return render_template('update_car.html', updatecar_error="Invalid file format! Allowed formats are: png, jpg, jpeg, gif", car= car)
    # Mettez à jour les informations de la voiture dans la base de données seulement si le champ 'picture' n'est pas vide
    cars_collection.update_one({'_id': ObjectId(car_id)}, {'$set': update_query})
    # Récupérez les informations de la voiture mise à jour depuis la base de données
    updated_car = cars_collection.find_one({'_id': ObjectId(car_id)})
    # Vérifiez si la voiture a été mise à jour avec succès
    if updated_car:
        return render_template('update_car.html', updatecar_valid="Car updated successfully!", car=updated_car)
    else:
        return render_template('update_car.html', updatecar_error="Failed to update car!", car= car)
        
'''
@app.route('/delete_car', methods=['GET'])
def delete_car():
    car_id = request.args.get('car_id')  # Récupérez l'identifiant de la voiture à partir de la requête GET
    cars_collection.delete_one({'_id': ObjectId(car_id)}) # Supprimez la voiture de la base de données
    return 'Car deleted successfully!'   '''



@app.route('/delete_car', methods=['GET'])
def delete_car():
    car_id = request.args.get('car_id')  # Récupérez l'identifiant de la voiture à partir de la requête GET
    cars_collection.update_one({'_id': ObjectId(car_id)}, {'$set': {'state': 'deleted'}})  # Marquez la voiture comme supprimée dans la base de données
    flash('Car deleted successfully!')  # Affichez un message de succès
    return redirect(url_for('cars'))  # Redirigez vers la page des voitures (ou une autre page appropriée)



@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Check if the username and password match
        user = users_collection.find_one({'email': email, 'password': password})
        if user:
            #flash('Login successful.', 'success')
             # Check the role of the user
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'manager':
                return redirect(url_for('dashboard_manager'))
            else:
                flash('Unknown role. Please contact support.', 'danger')
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')


@app.route('/logout/')
def logout():
    # Effacer toutes les données de session
    session.clear()
    # Rediriger vers la page de connexion
    return redirect(url_for('login'))


@app.route('/clients')
def clients():
    # Récupérer tous les clients depuis la collection dans la base de données MongoDB
    clients_data = clients_collection.find({'state': 'active'})
    # Convertir le curseur en une liste de dictionnaires
    clients_list = list(clients_data)
    # Passer les données des clients au modèle HTML pour affichage
    return render_template('clients.html', clients=clients_list)


@app.route('/delete_client/<client_id>', methods=['DELETE'])
def delete_client(client_id):
    # Convertir l'ID utilisateur en ObjectId
    client_id = ObjectId(client_id)
    # Mettre à jour l'état de l'utilisateur à "deleted"
    clients_collection.update_one({'_id': client_id}, {'$set': {'state': 'deleted'}})
    return '', 204  # Réponse HTTP 204 No Content pour indiquer que la mise à jour a réussi



@app.route('/modify_client', methods=['GET'])
def modify_client():
    client_id = request.args.get('client_id')  # Récupérez l'identifiant de la voiture à partir de la requête GET
    client = clients_collection.find_one({'_id': ObjectId(client_id)})  # Récupérez les informations de la voiture à partir de la base de données
    return render_template('modify_client.html', client=client)


@app.route('/modify_client', methods=['POST'])
def modify_client_BD():
    # Récupérer l'identifiant client depuis le formulaire
    client_id = request.form.get('id')
    # Vérifier si l'identifiant client est une chaîne vide
    if client_id:
        # Convertir l'identifiant client en ObjectId uniquement s'il n'est pas vide
        client_id = ObjectId(client_id)
        # Autres logiques pour la mise à jour du client dans la base de données
        clients_collection.update_one(
            {'_id': client_id},
            {'$set': {
                'name': request.form.get('clientname'),
                'CIN': request.form.get('clientCIN'),
                'email': request.form.get('clientEmail'),
                'phone': request.form.get('clientPhone'),
                'address': request.form.get('clientAddress')
            }}
        )
        return render_template('modify_client.html', updateClient_valid="Client updated successfully!", client=request.form)
    else:
        # Gérer le cas où l'identifiant client est vide
        return render_template('modify_client.html', updateClient_error="Client ID is missing or invalid!")



@app.route('/add_client', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        # Récupérer les données saisies par l'utilisateur depuis le formulaire
        clientname = request.form['clientname']
        clientCIN = request.form['clientCIN']
        clientEmail = request.form['clientEmail']
        clientPhone = request.form['clientPhone']
        clientAddress = request.form['clientAddress']
        # Créer un dictionnaire contenant les données du nouveau client
        new_client = {
            'name': clientname,
            'CIN': clientCIN,
            'email': clientEmail,
            'phone': clientPhone,
            'address': clientAddress,
            'state': 'active'
        }
        # Insérer le nouveau client dans la collection clients_collection
        clients_collection.insert_one(new_client)
        # Rediriger l'utilisateur vers la page des clients après l'ajout
        return redirect(url_for('clients'))
    # Si la méthode HTTP est GET, afficher simplement le formulaire
    return render_template('add_client.html')


@app.route('/add_reservation')  # Cette route correspond à la page pour les managers
def add_reservation():
    clients_data = clients_collection.find({'state': 'active'})
    clients_list = list(clients_data)
    cars_data = cars_collection.find({'state': 'active'})
    cars_list = list(cars_data)
    return render_template('add_reservation.html', clients=clients_list , cars=cars_list)


@app.route('/add_reserv', methods=['POST'])
def add_reserv():
    if request.method == 'POST':
        # Récupérer les données du formulaire soumises par l'utilisateur
        car_id = request.form['car_id']
        client_id = request.form['client_id']
        reservation_date = datetime.today().date().isoformat()  
        start_date = request.form['start_date']
        end_date = request.form['end_date']        
        # Vérifier si une réservation existe déjà pour la même voiture dans la même période
        existing_reservation = reservations_collection.find_one({
            'car_id': car_id,
            '$or': [
                {'start_date': {'$lte': start_date}, 'end_date': {'$gte': start_date}},
                {'start_date': {'$lte': end_date}, 'end_date': {'$gte': end_date}},
                {'start_date': {'$gte': start_date}, 'end_date': {'$lte': end_date}},
            ],
            'status': {'$eq': 'validée'}
        })
        # Vérifier si la voiture est disponible
        car = cars_collection.find_one({'_id': car_id, 'status': 'not available'})
        if existing_reservation or car:
            return render_template('add_reservation.html', reservation_error="La voiture n'est pas disponible pour la réservation.")
        # Insérer une nouvelle réservation dans la base de données
        reservations_collection.insert_one({
            'car_id': car_id,
            'client_id': client_id,
            'reservation_date': reservation_date,
            'start_date': start_date,
            'end_date': end_date,
            'status': 'en attente'  # ou tout autre statut initial que vous préférez
        })        
        # Rediriger l'utilisateur vers une page de confirmation ou une autre page appropriée
        return redirect(url_for('reservations'))


@app.route('/reservations')  
def reservations():
    # Récupérer toutes les réservations depuis la base de données
    reservations_data = reservations_collection.find({'status': 'en attente'})   
    # Convertir le curseur MongoDB en une liste de dictionnaires
    reservations_list = list(reservations_data)    
    # Passer les réservations au modèle HTML pour affichage
    return render_template('reservations.html', reservations=reservations_list)


@app.route('/manager_history')  
def reservations_history():
    # Récupérer toutes les réservations depuis la base de données
    reservations_data = reservations_collection.find({'status': {'$ne': 'en attente'}})
    deletedclients_data = clients_collection.find({'state': 'deleted'})
    deletedcars_data = cars_collection.find({'state': 'deleted'})
    # Convertir le curseur MongoDB en une liste de dictionnaires
    reservations_list = list(reservations_data)  
    deletedclients_list = list(deletedclients_data)
    deletedcars_list = list(deletedcars_data)  
    # Passer les réservations au modèle HTML pour affichage
    return render_template('/manager_history.html', reservations=reservations_list , clients=deletedclients_list , cars=deletedcars_list)



@app.route('/delete_reserv/<reserv_id>', methods=['DELETE'])
def delete_reserv(reserv_id):
    # Convertir l'ID de la réservation en ObjectId
    reserv_id = ObjectId(reserv_id)
    # Mettre à jour l'état de la réservation à "refusée"
    reservations_collection.update_one({'_id': reserv_id}, {'$set': {'status': 'refusée'}})
    return '', 204  # Réponse HTTP 204 No Content pour indiquer que la mise à jour a réussi


@app.route('/accept_reserv/<reserv_id>', methods=['PUT'])
def accept_reserv(reserv_id):
    # Convertir l'ID de la réservation en ObjectId
    reserv_id = ObjectId(reserv_id)    
    # Récupérer l'ID de la voiture à partir de la réservation
    reservation = reservations_collection.find_one({'_id': reserv_id})
    car_id = reservation['car_id']
    # Mettre à jour l'état de la réservation à "validée"
    reservations_collection.update_one({'_id': reserv_id}, {'$set': {'status': 'validée'}})    
    # Mettre à jour le statut de la voiture à "not available"
    print(car_id)
    cars_collection.update_one({'_id': ObjectId(car_id)}, {'$set': {'status': 'not available'}})    
    #return '', 204  # Réponse HTTP 204 No Content pour indiquer que la mise à jour a réussi
    return generate_invoice(reserv_id)

def generate_invoice(reserv_id):
    reservation = reservations_collection.find_one({'_id': ObjectId(reserv_id)})
    car_id = reservation['car_id']
    client_id = reservation['client_id']
    start_date = reservation['start_date']
    end_date = reservation['end_date']
    # Vous pouvez également récupérer les informations de la voiture et du client
    car = cars_collection.find_one({'_id': ObjectId(car_id)})
    client = clients_collection.find_one({'_id': ObjectId(client_id)})
    # Calculer le nombre de jours de location
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    if start_date == end_date:
        num_days = 1
    else:
        num_days = (end_date - start_date).days
    # Calculer le prix total en fonction du nombre de jours de location et du prix journalier de la voiture
    daily_price = car['price']
    if isinstance(daily_price, str):
        daily_price = float(daily_price) 
       
    total_price = num_days * daily_price
    # Créer un dictionnaire contenant toutes les données de la réservation
    reservation_data = {
        'reservation_id': reserv_id,
        'car': car,
        'client': client,
        'start_date': start_date,
        'end_date': end_date,
        'num_days': num_days,
        'total_price': total_price
    }
    # Rendre le modèle HTML avec les données de la réservation
    rendered_html = render_template('invoice_template.html', **reservation_data)
    # Convertir le HTML en PDF
    pdf = pdfkit.from_string(rendered_html, False)
    # Enregistrer le PDF sur le serveur
    pdf_filename = f'invoice_{reserv_id}.pdf'
    pdf_path = f'factures/{pdf_filename}'
    with open(pdf_path, 'wb') as f:
        f.write(pdf)
    # Renvoyer le PDF en tant que réponse
    return send_from_directory('factures', pdf_filename, as_attachment=True)



@app.route('/refuseReservation', methods=['POST'])
def refuse_reservation():
    # Récupérer les données envoyées
    data = request.json
    reservation_id = data.get('reservationId')
    reason = data.get('reason')
    # Enregistrer le motif de refus dans la base de données
    reservations_collection.update_one(
        { '_id': ObjectId(reservation_id) },
        { '$set': { 'status': 'refusée', 'reason': reason }}
    )
    return jsonify({ "message": "Motif de refus enregistré avec succès." }), 200

'''
@app.route('/dashboard_admin/')
def dashboard_admin():
    # Logique pour le tableau de bord de l'administrateur
    admin_count = users_collection.count_documents({'role': 'admin'})
    manager_count = users_collection.count_documents({'role': 'manager'})
    # Stockage des valeurs dans la session
    session['admin_count'] = admin_count
    session['manager_count'] = manager_count
    return render_template('adminDashbord.html', admin_count=admin_count, manager_count=manager_count )  '''
    
@app.route('/admin')  # Cette route correspond à la page pour les admins
def admin_dashboard():
 # Logique pour le tableau de bord de l'administrateur
    admin_count = users_collection.count_documents({'role': 'admin'})
    manager_count = users_collection.count_documents({'role': 'manager'})
    # Stockage des valeurs dans la session
    session['admin_count'] = admin_count
    session['manager_count'] = manager_count
    return render_template('adminDashbord.html', admin_count=admin_count, manager_count=manager_count )



@app.route('/dashboard_manager/')
def dashboard_manager():
    # Récupération des nombres de voitures, clients et réservations en attente
    car_count = cars_collection.count_documents({'state': 'active'})
    nbrclient = clients_collection.count_documents({'state': 'active'})
    nbrreservations = reservations_collection.count_documents({'status': 'en attente'})
    # Stockage des valeurs dans la session
    session['car_count'] = car_count
    session['client_count'] = nbrclient
    session['reservations_count'] = nbrreservations
    return render_template('managerDashbord.html', car_count=car_count, client_count=nbrclient, reservations_count=nbrreservations)
    return render_template('managerDashbord.html')


@app.route('/admin-view')
def admin_view():
    # Récupérer tous les utilisateurs depuis la collection dans la base de données MongoDB
    users_data = users_collection.find({'state': 'active'})
    users_list = list(users_data)  # Convertir le curseur en une liste de dictionnaires
    return render_template('admin_view.html', users=users_list)


@app.route('/admin-add', methods=['GET', 'POST'])
def admin_add():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        name = request.form['firstName']
        email = request.form['email']
        role = request.form['role']
        password = request.form['password']
        # Ajouter la date de création du compte
        created_at = datetime.today().date().isoformat()        
        # Insérer les données dans MongoDB
        new_user = {
            'name': name,
            'email': email,
            'role': role,
            'password': password,
            'state': 'active',
            'created_at': created_at
        }
        users_collection.insert_one(new_user)        
        # Rediriger vers une page de confirmation ou une autre page
        return redirect(url_for('admin_view'))
    # Si la méthode est GET, simplement rendre le template
    return render_template('admin_add.html')



@app.route('/admin-delete')
def admin_delete():
    # Récupérer tous les utilisateurs depuis la collection dans la base de données MongoDB
    users_data = users_collection.find()
    users_list = list(users_data)  # Convertir le curseur en une liste de dictionnaires
    return render_template('admin_delete.html', users=users_list)


@app.route('/admin-history')
def admin_history():
    # Récupérer les utilisateurs avec l'état "deleted" depuis la collection MongoDB
    deleted_users_data = users_collection.find({'state': 'deleted'})
    deleted_users_list = list(deleted_users_data)
    return render_template('admin_history.html', deleted_users=deleted_users_list)


@app.route('/delete_user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    # Convertir l'ID utilisateur en ObjectId
    user_id = ObjectId(user_id)
    # Mettre à jour l'état de l'utilisateur à "deleted"
    users_collection.update_one({'_id': user_id}, {'$set': {'state': 'deleted'}})
    return '', 204  # Réponse HTTP 204 No Content pour indiquer que la mise à jour a réussi


@app.route('/manager_history')
def manager_history():
    return render_template('manager_history.html')
