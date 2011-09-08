# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'SeatGroup', fields ['hallscheme', 'name']
        db.delete_unique('localsite_seatgroup', ['hallscheme_id', 'name'])

        # Adding model 'SeatSection'
        db.create_table('localsite_seatsection', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hallscheme', self.gf('django.db.models.fields.related.ForeignKey')(related_name='seatgroups', to=orm['localsite.HallScheme'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=25)),
        ))
        db.send_create_signal('localsite', ['SeatSection'])

        # Adding unique constraint on 'SeatSection', fields ['hallscheme', 'name']
        db.create_unique('localsite_seatsection', ['hallscheme_id', 'name'])

        # Deleting field 'SeatGroup.hallscheme'
        db.delete_column('localsite_seatgroup', 'hallscheme_id')

        # Renaming column for 'SeatGroup.section' to match new field type.
        db.rename_column('localsite_seatgroup', 'section', 'section_id')
        # Changing field 'SeatGroup.section'
        db.alter_column('localsite_seatgroup', 'section_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['localsite.SeatSection']))

        # Adding index on 'SeatGroup', fields ['section']
        db.create_index('localsite_seatgroup', ['section_id'])

        # Adding unique constraint on 'SeatGroup', fields ['section', 'name']
        db.create_unique('localsite_seatgroup', ['section_id', 'name'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'SeatGroup', fields ['section', 'name']
        db.delete_unique('localsite_seatgroup', ['section_id', 'name'])

        # Removing index on 'SeatGroup', fields ['section']
        db.delete_index('localsite_seatgroup', ['section_id'])

        # Removing unique constraint on 'SeatSection', fields ['hallscheme', 'name']
        db.delete_unique('localsite_seatsection', ['hallscheme_id', 'name'])

        # Deleting model 'SeatSection'
        db.delete_table('localsite_seatsection')

        # User chose to not deal with backwards NULL issues for 'SeatGroup.hallscheme'
        raise RuntimeError("Cannot reverse this migration. 'SeatGroup.hallscheme' and its values cannot be restored.")

        # Renaming column for 'SeatGroup.section' to match new field type.
        db.rename_column('localsite_seatgroup', 'section_id', 'section')
        # Changing field 'SeatGroup.section'
        db.alter_column('localsite_seatgroup', 'section', self.gf('django.db.models.fields.CharField')(max_length=25))

        # Adding unique constraint on 'SeatGroup', fields ['hallscheme', 'name']
        db.create_unique('localsite_seatgroup', ['hallscheme_id', 'name'])


    models = {
        'localsite.announcement': {
            'Meta': {'ordering': "['ordering', 'begin']", 'object_name': 'Announcement'},
            'begin': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'announcements'", 'to': "orm['localsite.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'localsite.city': {
            'Meta': {'ordering': "['ordering', 'name']", 'object_name': 'City'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '25'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '25', 'db_index': 'True'})
        },
        'localsite.event': {
            'Meta': {'ordering': "['min_date', 'max_date']", 'object_name': 'Event'},
            'hallscheme': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'events'", 'to': "orm['localsite.HallScheme']"}),
            'max_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'max_price': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'min_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'min_price': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['product.Product']", 'unique': 'True', 'primary_key': 'True'}),
            'tags': ('tagging.fields.TagField', [], {})
        },
        'localsite.eventdate': {
            'Meta': {'ordering': "['datetime', 'event']", 'unique_together': "(('event', 'datetime'),)", 'object_name': 'EventDate'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dates'", 'to': "orm['localsite.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'localsite.hall': {
            'Meta': {'ordering': "['city', 'name']", 'unique_together': "(('name', 'city'),)", 'object_name': 'Hall'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'halls'", 'to': "orm['localsite.City']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'})
        },
        'localsite.hallscheme': {
            'Meta': {'ordering': "['hall', 'name']", 'unique_together': "(('name', 'hall'),)", 'object_name': 'HallScheme'},
            'hall': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'schemes'", 'to': "orm['localsite.Hall']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'substrate': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'localsite.seatgroup': {
            'Meta': {'ordering': "['section', 'name']", 'unique_together': "(('section', 'name'),)", 'object_name': 'SeatGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'groups'", 'to': "orm['localsite.SeatSection']"})
        },
        'localsite.seatgroupprice': {
            'Meta': {'ordering': "['event', 'group']", 'unique_together': "(('group', 'event'),)", 'object_name': 'SeatGroupPrice'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'prices'", 'to': "orm['localsite.Event']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'prices'", 'to': "orm['localsite.SeatGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'localsite.seatlocation': {
            'Meta': {'ordering': "['group', 'row', 'col']", 'unique_together': "(('group', 'row', 'col'),)", 'object_name': 'SeatLocation'},
            'col': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'seats'", 'to': "orm['localsite.SeatGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'row': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'x_position': ('django.db.models.fields.IntegerField', [], {}),
            'y_position': ('django.db.models.fields.IntegerField', [], {})
        },
        'localsite.seatsection': {
            'Meta': {'ordering': "['hallscheme', 'name']", 'unique_together': "(('hallscheme', 'name'),)", 'object_name': 'SeatSection'},
            'hallscheme': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'seatgroups'", 'to': "orm['localsite.HallScheme']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        'localsite.ticket': {
            'Meta': {'ordering': "['datetime', 'event']", 'unique_together': "(('product', 'datetime', 'seat'), ('event', 'datetime', 'seat'))", 'object_name': 'Ticket'},
            'datetime': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tickets'", 'to': "orm['localsite.EventDate']"}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tickets'", 'to': "orm['localsite.Event']"}),
            'product': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['product.Product']", 'unique': 'True', 'primary_key': 'True'}),
            'seat': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['localsite.SeatLocation']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'freely'", 'max_length': '8'})
        },
        'product.category': {
            'Meta': {'ordering': "['site', 'parent__id', 'ordering', 'name']", 'unique_together': "(('site', 'slug'),)", 'object_name': 'Category'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'meta': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'child'", 'null': 'True', 'to': "orm['product.Category']"}),
            'related_categories': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'related_categories_rel_+'", 'null': 'True', 'to': "orm['product.Category']"}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'blank': 'True'})
        },
        'product.product': {
            'Meta': {'ordering': "('site', 'ordering', 'name')", 'unique_together': "(('site', 'sku'), ('site', 'slug'))", 'object_name': 'Product'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'also_purchased': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'also_purchased_rel_+'", 'null': 'True', 'to': "orm['product.Product']"}),
            'category': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['product.Category']", 'symmetrical': 'False', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'height': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'height_units': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items_in_stock': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '18', 'decimal_places': '6'}),
            'length': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'length_units': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'meta': ('django.db.models.fields.TextField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'related_items': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'related_items_rel_+'", 'null': 'True', 'to': "orm['product.Product']"}),
            'shipclass': ('django.db.models.fields.CharField', [], {'default': "'DEFAULT'", 'max_length': '10'}),
            'short_description': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'sku': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'taxClass': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['product.TaxClass']", 'null': 'True', 'blank': 'True'}),
            'taxable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'total_sold': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '18', 'decimal_places': '6'}),
            'weight': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'weight_units': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'width_units': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'})
        },
        'product.taxclass': {
            'Meta': {'object_name': 'TaxClass'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['localsite']
