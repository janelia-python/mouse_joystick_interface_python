(use-modules
 (guix packages)
 (guix git-download)
 (guix gexp)
 ((guix licenses) #:prefix license:)
 (guix build-system python)
 (gnu packages python-build)
 (gnu packages python-xyz)
 (gnu packages version-control)
 (guix-janelia packages python-guix)
 (guix-janelia packages python-janelia)
 )

(define %source-dir (dirname (current-filename)))

(define-public python-dev-package
  (package
   (name "python-dev-package")
   (version "dev")
   (source (local-file %source-dir
                       #:recursive? #t
                       #:select? (git-predicate %source-dir)))
   (build-system python-build-system)
   (native-inputs (list python-wheel python-twine python-ipython git))
   (propagated-inputs (list python-modular-client python-flatten-json))
   (home-page "")
   (synopsis "")
   (description "")
   (license license:gpl3+)))

python-dev-package
