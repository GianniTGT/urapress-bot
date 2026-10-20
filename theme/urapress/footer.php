<?php
/**
 * Fundi i faqes.
 *
 * @package UraPress
 */
?>
</div><!-- #content -->

<footer class="up-footer">
	<div class="up-wrap">
		<div class="up-footer__top">
			<div>
				<?php urapress_logo(); ?>
				<p class="up-footer__slogan"><?php esc_html_e( 'Lajmet nga Atdheu dhe jeta në Zvicër – në një vend, në gjuhën tonë.', 'urapress' ); ?></p>
				<a class="up-footer__social" href="https://www.facebook.com/1390417390820237" target="_blank" rel="noopener">
					<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M14 8h3V4h-3c-2.8 0-5 2.2-5 5v2H7v4h2v9h4v-9h3l1-4h-4V9c0-.6.4-1 1-1z"/></svg>
					<?php esc_html_e( 'Na ndiqni në Facebook', 'urapress' ); ?>
				</a>
			</div>
			<div class="up-footer__cats">
				<ul>
					<?php
					foreach ( urapress_main_categories() as $name ) {
						$term = urapress_category_by_name( $name );
						if ( $term ) {
							printf( '<li><a href="%s">%s</a></li>', esc_url( get_category_link( $term ) ), esc_html( $term->name ) );
						}
					}
					?>
				</ul>
			</div>
		</div>
		<div class="up-footer__bottom">
			<span>&copy; <?php echo esc_html( gmdate( 'Y' ) ); ?> UraPress.ch</span>
			<?php
			wp_nav_menu(
				array(
					'theme_location' => 'footer',
					'container'      => false,
					'depth'          => 1,
					'fallback_cb'    => '__return_false',
				)
			);
			?>
		</div>
	</div>
</footer>

<?php wp_footer(); ?>
</body>
</html>
