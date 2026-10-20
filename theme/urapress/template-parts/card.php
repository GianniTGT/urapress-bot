<?php
/**
 * Karta e një artikulli.
 *
 * Args: variant (lead|default|row), size (madhësia e fotos), excerpt (bool), heading (h2|h3).
 *
 * @package UraPress
 */

$urapress_args    = wp_parse_args(
	$args ?? array(),
	array(
		'variant' => 'default',
		'size'    => 'urapress-card',
		'excerpt' => false,
		'heading' => 'h3',
	)
);
$urapress_variant = $urapress_args['variant'];
$urapress_heading = in_array( $urapress_args['heading'], array( 'h2', 'h3' ), true ) ? $urapress_args['heading'] : 'h3';
$urapress_cat     = urapress_primary_category();

urapress_shown( get_the_ID() );
?>
<article <?php post_class( 'up-card up-card--' . $urapress_variant . ( 0 === strpos( $urapress_variant, 'overlay' ) ? ' up-card--overlay' : '' ) ); ?>>
	<a class="up-card__media" href="<?php the_permalink(); ?>" tabindex="-1" aria-hidden="true">
		<?php if ( has_post_thumbnail() ) : ?>
			<?php the_post_thumbnail( $urapress_args['size'], array( 'alt' => '', 'loading' => 'lead' === $urapress_variant ? 'eager' : 'lazy' ) ); ?>
		<?php else : ?>
			<span class="up-card__noimg"><svg viewBox="0 0 120 60" aria-hidden="true" fill="none" stroke="#16181D" stroke-linecap="round"><path d="M38 48V31M60 48V20M82 48V31" stroke-width="2.5"/><path d="M12 48Q60 -2 108 48" stroke="#D7141A" stroke-width="6"/><path d="M8 48h104" stroke-width="5"/></svg></span>
		<?php endif; ?>
		<?php $urapress_badge = urapress_post_badge(); ?>
		<?php if ( $urapress_badge ) : ?>
			<span class="up-card__badge up-card__badge--<?php echo esc_attr( $urapress_badge[0] ); ?>"><?php echo esc_html( $urapress_badge[1] ); ?></span>
		<?php endif; ?>
		<?php $urapress_nc = (int) get_comments_number(); ?>
		<?php if ( $urapress_nc > 0 ) : ?>
			<span class="up-card__comments" aria-hidden="true">
				<svg viewBox="0 0 24 24" width="13" height="13" fill="currentColor" aria-hidden="true"><path d="M4 4h16a1 1 0 0 1 1 1v11a1 1 0 0 1-1 1H9l-5 4v-4H4a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1z"/></svg><?php echo esc_html( $urapress_nc ); ?>
			</span>
		<?php endif; ?>
	</a>
	<div class="up-card__body">
		<?php if ( $urapress_cat && 'row' !== $urapress_variant ) : ?>
			<a class="up-card__cat" href="<?php echo esc_url( get_category_link( $urapress_cat ) ); ?>"><?php echo esc_html( $urapress_cat->name ); ?></a>
		<?php endif; ?>
		<<?php echo $urapress_heading; // phpcs:ignore ?> class="up-card__title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></<?php echo $urapress_heading; // phpcs:ignore ?>>
		<?php if ( $urapress_args['excerpt'] ) : ?>
			<p class="up-card__excerpt"><?php echo esc_html( get_the_excerpt() ); ?></p>
		<?php endif; ?>
		<span class="up-card__meta"><?php echo urapress_time(); // phpcs:ignore ?></span>
	</div>
</article>
