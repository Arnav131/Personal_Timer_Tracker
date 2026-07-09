const SIZE_CLASS = {
  xs: 'pixel-icon--xs',
  sm: 'pixel-icon--sm',
  md: 'pixel-icon--md',
  lg: 'pixel-icon--lg',
  xl: 'pixel-icon--xl',
};

export default function PixelIcon({ name, size = 'sm', className = '', alt = '', ...props }) {
  const classes = ['pixel-icon', SIZE_CLASS[size] || SIZE_CLASS.sm, className]
    .filter(Boolean)
    .join(' ');
  const accessibilityProps = alt
    ? { alt }
    : { alt: '', 'aria-hidden': 'true' };

  return (
    <img
      src={`/pixel-icons/${name}.png`}
      className={classes}
      draggable="false"
      {...accessibilityProps}
      {...props}
    />
  );
}
