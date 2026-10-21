<?php
/**
 * ZaZu – Comic-Seite: neueste Comics zuerst, ganz gross.
 *
 * @package UraPress
 */

get_header();
?>
<main class="up-wrap up-zazu">
	<header class="up-zazu__head">
		<h1 class="up-zazu__title">ZaZu</h1>
		<p class="up-zazu__sub">Kotelja më e famshme e diasporës – me katër gishta te këmbët e pasme dhe pa durim për bowling.</p>
	</header>
	<?php
	if ( have_posts() ) :
		while ( have_posts() ) :
			the_post();
			?>
			<article class="up-zazu__item">
				<a class="up-zazu__date" href="<?php the_permalink(); ?>"><?php echo esc_html( urapress_sq_date( (int) get_post_time( 'U' ), false, true ) ); ?></a>
				<div class="up-content"><?php the_content(); ?></div>
				<?php urapress_share( get_permalink(), get_the_title() . ' 😺' ); ?>
			</article>
			<?php
		endwhile;
		?>
		<nav class="up-zazu-nav">
			<?php
			$urapress_older = get_next_posts_link( '← Më të vjetra' );
			$urapress_newer = get_previous_posts_link( 'Më të reja →' );
			echo $urapress_older ? $urapress_older : '<span></span>'; // phpcs:ignore
			echo $urapress_newer ? $urapress_newer : '<span></span>'; // phpcs:ignore
			?>
		</nav>
	<?php else : ?>
		<p>ZaZu po fle. Së shpejti skica e parë.</p>
	<?php endif; ?>
</main>
<?php
get_footer();
