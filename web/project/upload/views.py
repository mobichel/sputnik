from flask import Blueprint, render_template, abort, request, redirect, url_for, flash, send_from_directory
import glob, os, json
from ..visualizations.forms import AddVisualizationForm
from ..templates.forms import AddTemplateForm
from ..dashboards.forms import AddDashboardForm
from ..utils.uploadsets import upload_plugins, upload_images, \
    upload_exported_templates, upload_exported_options, upload_exported_dashboards
from ..models import Visualizations, Templates, Dashboards
from flask_security import login_required, auth_token_required, current_user
from flask_principal import Permission, RoleNeed


blueprint = Blueprint('upload', __name__, url_prefix='/upload', static_url_path='/assets', static_folder='assets/community', template_folder='templates')

# Create a permission with a single Need, in this case a RoleNeed.
admin_permission = Permission(RoleNeed('admin'))
editor_permission = Permission(RoleNeed('editor'))


@blueprint.route('/visualizations', methods=['GET', 'POST'])
@login_required
#@admin_permission.require(http_exception=403)
def add_visualization():

    form = AddVisualizationForm()

    if request.method == 'POST' and 'vis_image' in request.files:

        alias = current_user['email'].split('@')[0]
        product = form.vis_type.data

        filename1 = upload_images.save(request.files['vis_image'], folder='visualizations/'+product+'/screenshot/'+alias)
        filename2 = upload_images.save(request.files['vis_options'], folder='visualizations/'+product+'/screenshot/'+alias)
        filename3 = upload_plugins.save(request.files['vis_manifest'], folder='visualizations/'+product+'/plugin/'+alias)

        image_src = "_uploads/community/{}".format(filename1)
        image_edit = "_uploads/community/{}".format(filename2)
        plugin_src = "_uploads/community/{}".format(filename3)

        name = "{}-{}".format(form.vis_title.data.replace(" ", ""), alias)

        viz =Visualizations(title=form.vis_title.data, name=name, short_desc=form.vis_short_desc.data,
                            desc=form.vis_desc.data, rating=form.vis_rating.data, author=form.vis_credit.data, contributor=current_user.email,
                            image_src=image_src, image_edit=image_edit, plugin_src=plugin_src)

        viz.save()

        return redirect(url_for('visualizations.get_visualization_list'))

    return render_template('upload/add_visualization.html', form=form)


@blueprint.route('/templates', methods=['GET', 'POST'])
@login_required
#@admin_permission.require(http_exception=403)
def add_template():

    form = AddTemplateForm()

    if request.method == 'POST' and 'template_export' in request.files and 'ss_options_export' in request.files:

        alias = current_user['email'].split('@')[0]
        product = form.template_type.data

        filename1 = upload_exported_templates.save(request.files['template_export'], folder='templates/'+product+'/definition/'+alias)

        if request.files['template_image'].filename == '':
            print "No available screenshot"
            image_src = ''
        else:
            filename2 = upload_images.save(request.files['template_image'],
                                           folder='templates/'+product+'/screenshot/'+alias)

            image_src = "_uploads/community/{}".format(filename2)

        filename3 = upload_exported_options.save(request.files['ss_options_export'], folder='templates/'+product+'/option/'+alias)
        ss_option_src = "_uploads/community/{}".format(filename3)
        template_src = "_uploads/community/{}".format(filename1)
        template_src_file = "{}/{}".format(blueprint.static_folder, filename1)


        with open(template_src_file) as fh:
            tmp = json.load(fh)
            if 'definition' in tmp:
                definition = tmp['definition']
                name = definition['guid']
            elif 'template' in tmp:
                definition = tmp['template'][0]['definition']
                name = definition['guid']
            else:
                print 'Template definition not accurate'
                name = None

        metadata = {'image_src':image_src, 'contributor':current_user.email, 'author': form.template_support.data,
                    'template_src':template_src, 'ss_option_src':ss_option_src}

        template = Templates(name=name, definition=definition, rating=form.template_rating.data, metadata=metadata)

        template.save()

        return redirect(url_for('templates.get_template_list'))
        #return redirect(url_for('upload.complete', user_email=current_user.email))

    return render_template('upload/add_template.html', form=form)


@blueprint.route('/dashboards', methods=['GET', 'POST'])
@login_required
#@admin_permission.require(http_exception=403)
def add_dashboard():

    form = AddDashboardForm()

    if request.method == 'POST' and 'dashboard_image' in request.files and 'dashboard_metadata' in request.files:

        alias = current_user['email'].split('@')[0]
        product = form.dashboard_type.data

        new_dashboard = {}

        filename1 = upload_exported_dashboards.save(request.files['dashboard_metadata'], folder='dashboards/'+product+'/metadata/'+alias)
        filename2 = upload_images.save(request.files['dashboard_image'], folder='dashboards/'+product+'/screenshot/'+alias)
        filename3 = upload_exported_dashboards.save(request.files['dashboard_export'], folder='dashboards/'+product+'/export/'+alias)

        image_src = "_uploads/community/{}".format(filename2)
        download_link = "_uploads/community/{}".format(filename3)
        dashboard_metadata_file = "{}/{}".format(blueprint.static_folder, filename1)

        with open(dashboard_metadata_file) as fh:
            tmp = json.load(fh)

            new_dashboard['title'] = tmp['title']
            new_dashboard['name'] ="{}-{}".format(tmp['title'].replace(" ", "_"), alias)
            new_dashboard['short_desc'] = tmp['short_desc']
            new_dashboard['rating'] = tmp['rating']
            new_dashboard['tags'] = tmp['tags']
            new_dashboard['overview'] = tmp['overview']
            new_dashboard['prerequisites'] = tmp['prerequisites']
            new_dashboard['author'] = tmp['overview']['author']
            new_dashboard['product'] = form.dashboard_type.data
            new_dashboard['contributor'] = current_user.email
            new_dashboard['download_link'] = download_link
            new_dashboard['image_src'] = image_src

        dashboard = Dashboards(**new_dashboard)
        dashboard.save()
        return redirect(url_for('dashboards.get_dashboard_list'))

    return render_template('upload/add_dashboard.html', form=form)



'''
# Route that will process the file upload
@blueprint.route('/', methods=['GET','POST'])
@login_required
def upload():
    form = request.form
    if request.method == 'POST':
        target = "{}/users/{}".format(blueprint.root_path, current_user.email)
        try:
            os.mkdir(target)
        except OSError as e:
            if e.errno == errno.EEXIST:
                print("Couldn't create directory {}".format(target))

        for upload in request.files.getlist("file"):
            filename = upload.filename.rsplit("/")[0]
            destination = '/'.join([target, filename])
            print( "Accepting: {}\n and saving to: {}".format(filename, destination))
            upload.save(destination)

        return redirect(url_for('upload.complete', user_email=current_user.email))
    return render_template('upload/post.html', form=form)


@blueprint.route("/files/<user_email>", methods=['GET', 'POST'])
def complete(user_email):
    location = "{}/assets/user/screenshots/{}".format(blueprint.root_path, user_email)

    if not os.path.isdir(location):
        return "Error! {} not found!".format(location)

    print url_for('static', filename='test/')
    print url_for('upload.static', filename='test/')

    files = []
    for file in glob.glob("{}/*.*".format(location)):
        fname = file.split(os.sep)[-1]
        files.append(fname)

    return render_template('upload/complete.html', user_email=user_email, files=files)
'''
