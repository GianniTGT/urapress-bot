<?php
/**
 * Komentet e artikullit.
 *
 * @package UraPress
 */

if ( post_password_required() ) {
	return;
}

$urapress_count = (int) get_comments_number();
?>
<section id="comments" class="up-comments">
	<div class="up-section__head">
		<h2 class="up-section__title">
			<?php
			echo esc_html(
				$urapress_count
					? sprintf( 'Komentet (%d)', $urapress_count )
					: __( 'Komentet', 'urapress' )
			);
			?>
		</h2>
	</div>

	<?php if ( $urapress_count ) : ?>
		<ol class="up-comments__list">
			<?php
			wp_list_comments(
				array(
					'style'       => 'ol',
					'short_ping'  => true,
					'avatar_size' => 40,
					'reply_text'  => __( 'Përgjigju', 'urapress' ),
				)
			);
			?>
		</ol>
		<?php the_comments_pagination( array( 'prev_text' => '‹', 'next_text' => '›' ) ); ?>
	<?php elseif ( comments_open() ) : ?>
		<p class="up-comments__empty"><?php esc_html_e( 'Ende nuk ka komente. Bëhu i pari që e komenton këtë lajm.', 'urapress' ); ?></p>
	<?php endif; ?>

	<?php if ( comments_open() ) : ?>
		<?php
		$urapress_commenter = wp_get_current_commenter();
		comment_form(
			array(
				'title_reply'          => __( 'Lini një koment', 'urapress' ),
				'title_reply_to'       => __( 'Përgjigju %s', 'urapress' ),
				'cancel_reply_link'    => __( 'Anulo', 'urapress' ),
				'label_submit'         => __( 'Dërgo komentin', 'urapress' ),
				'class_submit'         => 'up-btn',
				'comment_notes_before' => '<p class="up-comments__note">' . esc_html__( 'Emaili juaj nuk publikohet. Komentet shfaqen pasi t\'i shqyrtojë redaksia. Komentet fyese, raciste ose me reklama fshihen.', 'urapress' ) . '</p>',
				'comment_field'        => '<p class="comment-form-comment"><label for="comment">' . esc_html__( 'Komenti juaj', 'urapress' ) . ' *</label><textarea id="comment" name="comment" rows="5" maxlength="2000" required></textarea></p>',
				'fields'               => array(
					'author'  => '<p class="comment-form-author"><label for="author">' . esc_html__( 'Emri', 'urapress' ) . ' *</label><input id="author" name="author" type="text" value="' . esc_attr( $urapress_commenter['comment_author'] ) . '" maxlength="80" autocomplete="name" required></p>',
					'email'   => '<p class="comment-form-email"><label for="email">' . esc_html__( 'Email', 'urapress' ) . ' *</label><input id="email" name="email" type="email" value="' . esc_attr( $urapress_commenter['comment_author_email'] ) . '" maxlength="100" autocomplete="email" required></p>',
					'cookies' => '<p class="comment-form-cookies-consent"><input id="wp-comment-cookies-consent" name="wp-comment-cookies-consent" type="checkbox" value="yes"><label for="wp-comment-cookies-consent">' . esc_html__( 'Ruaj emrin dhe emailin në këtë shfletues për komentin e radhës.', 'urapress' ) . '</label></p>',
				),
			)
		);
		?>
	<?php endif; ?>
</section>
