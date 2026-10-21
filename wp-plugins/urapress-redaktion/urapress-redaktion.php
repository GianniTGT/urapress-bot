<?php
/**
 * Plugin Name: UraPress Redaktion
 * Description: Einfache Redaktionsmaske fuer Beitraege mit Text, Fett, Kursiv, Medien und Beitragsbild.
 * Version: 1.0.0
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }

add_action( 'admin_menu', function () {
    add_menu_page( 'Redaktion', 'Redaktion', 'edit_posts', 'urapress-redaktion', 'urapress_redaktion_page', 'dashicons-edit-page', 4 );
} );

add_action( 'admin_enqueue_scripts', function ( $hook ) {
    if ( 'toplevel_page_urapress-redaktion' === $hook ) { wp_enqueue_media(); }
} );

function urapress_redaktion_page() {
    if ( ! current_user_can( 'edit_posts' ) ) { return; }
    $notice  = '';
    $post_id = isset( $_GET['edit'] ) ? (int) $_GET['edit'] : 0;

    if ( ! empty( $_POST['urapress_save'] ) ) {
        check_admin_referer( 'urapress_redaktion' );
        $post_id = isset( $_POST['post_id'] ) ? (int) $_POST['post_id'] : 0;
        $data    = array(
            'post_title'   => sanitize_text_field( wp_unslash( $_POST['title'] ?? '' ) ),
            'post_content' => wp_kses_post( wp_unslash( $_POST['content'] ?? '' ) ),
            'post_status'  => 'publish',
            'post_type'    => 'post',
        );
        if ( $post_id ) { $data['ID'] = $post_id; }
        $saved = $post_id ? wp_update_post( $data, true ) : wp_insert_post( $data, true );
        if ( is_wp_error( $saved ) ) {
            $notice = '<div class="notice notice-error"><p>Fehler: ' . esc_html( $saved->get_error_message() ) . '</p></div>';
        } else {
            $post_id = (int) $saved;
            $cat     = isset( $_POST['category'] ) ? (int) $_POST['category'] : 0;
            if ( $cat ) { wp_set_post_categories( $post_id, array( $cat ) ); }
            $thumb = isset( $_POST['thumb_id'] ) ? (int) $_POST['thumb_id'] : 0;
            if ( $thumb ) { set_post_thumbnail( $post_id, $thumb ); } else { delete_post_thumbnail( $post_id ); }
            $notice = '<div class="notice notice-success"><p>Gespeichert und veröffentlicht. <a href="' . esc_url( get_permalink( $post_id ) ) . '" target="_blank">Beitrag ansehen</a></p></div>';
        }
    }

    $post = $post_id ? get_post( $post_id ) : null;
    if ( $post && 'post' !== $post->post_type ) { $post = null; $post_id = 0; }
    $title     = $post ? $post->post_title : '';
    $content   = $post ? $post->post_content : '';
    $cat_id    = 0;
    $thumb_id  = 0;
    if ( $post ) {
        $cats     = get_the_category( $post->ID );
        $cat_id   = $cats ? (int) $cats[0]->term_id : 0;
        $thumb_id = (int) get_post_thumbnail_id( $post->ID );
    }
    $thumb_src = $thumb_id ? wp_get_attachment_image_url( $thumb_id, 'medium' ) : '';
    $recent    = get_posts( array( 'numberposts' => 40, 'post_status' => array( 'publish', 'draft' ) ) );
    $cats_all  = get_categories( array( 'hide_empty' => false ) );
    ?>
    <div class="wrap">
        <h1>Redaktion</h1>
        <?php echo $notice; // phpcs:ignore ?>
        <form method="get" style="margin:12px 0">
            <input type="hidden" name="page" value="urapress-redaktion">
            <select name="edit" onchange="this.form.submit()">
                <option value="0">— Neuer Beitrag —</option>
                <?php foreach ( $recent as $r ) : ?>
                    <option value="<?php echo (int) $r->ID; ?>" <?php selected( $post_id, $r->ID ); ?>><?php echo esc_html( $r->post_title ); ?></option>
                <?php endforeach; ?>
            </select>
        </form>

        <form method="post">
            <?php wp_nonce_field( 'urapress_redaktion' ); ?>
            <input type="hidden" name="urapress_save" value="1">
            <input type="hidden" name="post_id" value="<?php echo (int) $post_id; ?>">
            <input type="hidden" name="thumb_id" id="thumb_id" value="<?php echo (int) $thumb_id; ?>">

            <p><label><strong>Titel</strong><br>
                <input type="text" name="title" value="<?php echo esc_attr( $title ); ?>" style="width:100%;font-size:18px;padding:8px"></label></p>

            <p><strong>Text</strong></p>
            <?php wp_editor( $content, 'content', array( 'textarea_name' => 'content', 'media_buttons' => true, 'textarea_rows' => 18, 'teeny' => false, 'quicktags' => false ) ); ?>

            <p style="margin-top:20px"><label><strong>Rubrik</strong><br>
                <select name="category">
                    <option value="0">— wählen —</option>
                    <?php foreach ( $cats_all as $c ) : ?>
                        <option value="<?php echo (int) $c->term_id; ?>" <?php selected( $cat_id, $c->term_id ); ?>><?php echo esc_html( $c->name ); ?></option>
                    <?php endforeach; ?>
                </select></label></p>

            <p><strong>Beitragsbild</strong><br>
                <img id="thumb-preview" src="<?php echo esc_url( $thumb_src ); ?>" style="max-width:300px;<?php echo $thumb_src ? '' : 'display:none;'; ?>"><br>
                <button type="button" class="button" id="thumb-pick">Foto wählen / hochladen</button>
                <button type="button" class="button" id="thumb-remove">Foto entfernen</button></p>

            <p><button type="submit" class="button button-primary button-hero">Veröffentlichen</button></p>
        </form>
    </div>
    <script>
    jQuery( function ( $ ) {
        var frame;
        $( '#thumb-pick' ).on( 'click', function ( e ) {
            e.preventDefault();
            if ( frame ) { frame.open(); return; }
            frame = wp.media( { title: 'Foto wählen', multiple: false, library: { type: 'image' } } );
            frame.on( 'select', function () {
                var a = frame.state().get( 'selection' ).first().toJSON();
                $( '#thumb_id' ).val( a.id );
                $( '#thumb-preview' ).attr( 'src', ( a.sizes && a.sizes.medium ) ? a.sizes.medium.url : a.url ).show();
            } );
            frame.open();
        } );
        $( '#thumb-remove' ).on( 'click', function () { $( '#thumb_id' ).val( 0 ); $( '#thumb-preview' ).hide(); } );
    } );
    </script>
    <?php
}