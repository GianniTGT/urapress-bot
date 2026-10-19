<?php
/**
 * Formulari i kërkimit.
 *
 * @package UraPress
 */

$urapress_id = wp_unique_id( 'up-s-' );
?>
<form role="search" method="get" class="up-search" action="<?php echo esc_url( home_url( '/' ) ); ?>">
	<label class="screen-reader-text" for="<?php echo esc_attr( $urapress_id ); ?>"><?php esc_html_e( 'Kërko', 'urapress' ); ?></label>
	<input type="search" id="<?php echo esc_attr( $urapress_id ); ?>" name="s" value="<?php echo esc_attr( get_search_query() ); ?>" placeholder="<?php esc_attr_e( 'Kërko lajme…', 'urapress' ); ?>">
	<button type="submit" aria-label="<?php esc_attr_e( 'Kërko', 'urapress' ); ?>">
		<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
	</button>
</form>
