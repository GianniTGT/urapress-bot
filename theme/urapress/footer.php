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
